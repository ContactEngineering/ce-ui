<script setup>
/*
 * Vue component that wraps a Bokeh plot and adds elements for controlling that plot's appearance.
 * - Categories: Each dataset can be assigned multiple *categories*. Each category receives interactive chips
 *   that allow showing/hiding all datasets belonging to a specific value of this category.
 */

import {v4 as uuid4} from 'uuid';
import {computed, onBeforeUnmount, onMounted, ref, watch} from "vue";

import {
    AjaxDataSource,
    HoverTool,
    Legend,
    LegendItem,
    Palettes,
    Plotting,
    SaveTool,
    Scatter,
    TapTool
} from '@bokeh/bokehjs';

import {
    BButton,
    BTab,
    BTabs
} from "bootstrap-vue-next";

import {applyDefaultBokehStyle} from "@/utils/bokeh";
import {
    assignElementColors,
    assignElementDashes,
    buildCategoryElements,
    legendLabel
} from "@/utils/plot";

import BokehPlotOptions from "@/components/ui/BokehPlotOptions.vue";

// Bookkeeping of pending ajax requests for displaying spinners
const nbPendingAjaxRequests = defineModel('nbPendingAjaxRequests', {required: false, default: 0});

// Emitted when a dataset is selected
const emit = defineEmits(['selected']);

const props = defineProps({
    categories: {
        type: Array, default() {
            return [];
        }
    },
    plots: {
        type: Array, default() {
            return [{
                title: "default",
                xData: null,
                yData: null,
                auxiliaryDataColumns: null,
                alphaData: null,
                xAxisType: "linear",
                yAxisType: "linear",
                xAxisLabel: "x",
                yAxisLabel: "y"
            }]
        }
    },
    dataSources: {
        type: Array, default() {
            return [];
        }
    },
    outputBackend: String,
    height: {type: Number, default: 300},
    width: {type: Number, default: null},
    showSymbols: {type: Boolean, default: true},
    sizingMode: {type: String, default: "scale_width"},
    aspectRatio: {type: Number, default: 2},
    uid: {
        type: String, default() {
            return uuid4();
        }
    },
    selectable: {type: Boolean, default: false},
    optionsWidgets: {
        type: Array, default: function () {
            return ["layout", "legend", "lineWidth", "symbolSize", "opacity"];
        }
    },
    functionTitle: {type: String, default: "bokeh_plot"}
});

// GUI logic
const _layout = ref("web");
const _legendLocation = ref("off");
const _symbolSize = ref(10);
const _opacity = ref(0.4);
const _lineWidth = ref(1);
const showOptions = ref(false);

// Component lifecycle tracking for teardown safety
const isMounted = ref(false);

// Reorganized plot information
let _bokehFigures = [];  // Stores Bokeh figure, line and symbol objects
let _bokehViews = [];  // Stores the views returned by `Plotting.show` so we can dispose them on unmount
let _categoryElements = ref([]);  // Sorted categories with selectable elements
let _categoryElementSelections = [];  // Flags which categories are selected

// Colors
const _parentColorPalette = Palettes.Greys256;  // Surfaces are shown in black/grey
const _childColorPalette = Palettes.Plasma256;  // Plasma is used for topographies

onMounted(() => {
    isMounted.value = true;
    if (props.dataSources.length > 0) {
        createFigures();
        updateCategoryElements();
        createPlots();
    }
});

watch(_layout, (layout) => {
    switch (layout) {
        case 'web':
            for (const figure of _bokehFigures) {
                figure.figure.sizing_mode = props.sizingMode;
                figure.figure.aspect_ratio = props.aspectRatio;
                figure.figure.height = props.height;
            }
            _symbolSize.value = 10;
            break;
        case 'print-single':
            for (const figure of _bokehFigures) {
                figure.figure.sizing_mode = "fixed";
                figure.figure.width = 600;
                figure.figure.height = 300;
            }
            _symbolSize.value = 5;
            break;
        case 'print-double':
            for (const figure of _bokehFigures) {
                figure.figure.sizing_mode = "fixed";
                figure.figure.width = 400;
                figure.figure.height = 250;
            }
            _symbolSize.value = 5;
            break;
    }

    refreshPlots();
});

watch([_opacity, _symbolSize, _lineWidth], () => {
    refreshPlots();
});

watch(_legendLocation, (newVal) => {
    const visible = newVal !== "off";
    for (const figure of _bokehFigures) {
        figure.legend.visible = visible;
        if (visible) {
            figure.legend.location = newVal;
        }
    }
});

watch(() => props.dataSources, (newVal, oldVal) => {
    let hasChanged = !oldVal || newVal.length !== oldVal.length;
    if (!hasChanged) {
        for (const [index, val] of newVal.entries()) {
            hasChanged = hasChanged || (val.url !== oldVal[index].url);
        }
    }
    if (hasChanged && isMounted.value) {
        if (_bokehFigures.length === 0) {
            createFigures();
        }
        updateCategoryElements();
        createPlots();
    }
});

function updateCategoryElements() {
    _categoryElementSelections = [];
    _categoryElements.value.length = 0;

    const elementsPerCategory = buildCategoryElements(props.categories, props.dataSources);

    if (elementsPerCategory.length > 0) {
        assignElementColors(elementsPerCategory[0], _parentColorPalette, _childColorPalette);
        if (elementsPerCategory[1] != null) {
            assignElementDashes(elementsPerCategory[1]);
        }
    }

    for (const [categoryIndex, category] of props.categories.entries()) {
        const selections = elementsPerCategory[categoryIndex].map(element => ref(element.visible));
        _categoryElementSelections.push(selections);

        _categoryElements.value.push({
            key: category.key,
            title: category.title,
            elements: elementsPerCategory[categoryIndex].map((element, elementIndex) => ({
                ...element,
                selected: computed({
                    get() {
                        return _categoryElementSelections[categoryIndex][elementIndex].value;
                    },
                    set(value) {
                        setPlotVisibility(categoryIndex, elementIndex, value);
                        _categoryElementSelections[categoryIndex][elementIndex].value = value;
                    }
                })
            }))
        });
    }
}

function groupCategoryElements(elements) {
    const hasHierarchy = elements.some(e => e.hasParent);
    if (!hasHierarchy) {
        return [{ parent: null, children: elements }];
    }

    const groups = [];
    let currentGroup = null;

    for (const element of elements) {
        if (!element.hasParent) {
            currentGroup = {
                parent: element,
                children: []
            };
            groups.push(currentGroup);
        } else {
            if (!currentGroup) {
                currentGroup = {
                    parent: null,
                    children: []
                };
                groups.push(currentGroup);
            }
            currentGroup.children.push(element);
        }
    }
    return groups;
}

function toggleGroupParent(group) {
    if (!group.parent) return;
    const nextState = !group.parent.selected;
    group.parent.selected = nextState;
    for (const child of group.children) {
        child.selected = nextState;
    }
}

function destroyBokehViews() {
    for (const viewOrPromise of _bokehViews) {
        Promise.resolve(viewOrPromise).then(view => {
            try {
                if (view != null && typeof view.remove === "function") {
                    view.remove();
                }
            } catch (e) {
                /* Ignore errors during teardown */
            }
        }).catch(() => { /* Ignore rejected view promises */ });
    }
    _bokehViews.length = 0;

    for (const figure of _bokehFigures) {
        try {
            const doc = figure.figure?.document;
            if (doc != null && typeof doc.clear === "function") {
                doc.clear();
            }
        } catch (e) {
            /* Ignore errors during teardown */
        }
        figure.lines.length = 0;
        figure.symbols.length = 0;
        figure.sources.length = 0;
        figure.legendItems.length = 0;
    }
    _bokehFigures.length = 0;
}

function createFigures() {
    destroyBokehViews();

    for (const plot of props.plots) {
        let tools = ["pan", "reset", "wheel_zoom", "box_zoom",
            new HoverTool({
                'tooltips': [
                    ['index', '$index'],
                    ['(x,y)', '($x,$y)'],
                    ['subject', '@subjectName'],
                    ['series', '@seriesName'],
                ]
            })
        ];

        if (props.selectable) {
            tools.push(new TapTool({
                behavior: "select",
                callback: {execute: onTap}
            }));
        }

        const saveTool = new SaveTool({filename: props.functionTitle.replace(" ", "_").toLowerCase()});
        tools.push(saveTool);

        const xAxisType = plot.xAxisType == null ? "linear" : plot.xAxisType;
        const yAxisType = plot.yAxisType == null ? "linear" : plot.yAxisType;

        const figure = new Plotting.Figure({
            height: props.height,
            sizing_mode: props.sizingMode,
            aspect_ratio: props.aspectRatio,
            x_axis_label: plot.xAxisLabel == null ? "x" : plot.xAxisLabel,
            y_axis_label: plot.yAxisLabel == null ? "y" : plot.yAxisLabel,
            x_axis_type: xAxisType,
            y_axis_type: yAxisType,
            tools: tools,
            output_backend: props.outputBackend
        });

        applyDefaultBokehStyle(figure);

        _bokehFigures.push({
            figure: figure,
            save: saveTool,
            lines: [],
            symbols: [],
            sources: [],
            legendItems: []
        });
    }

    for (const [index, figure] of _bokehFigures.entries()) {
        figure.legend = new Legend({items: figure.legendItems, visible: false});
        figure.figure.add_layout(figure.legend);
        _bokehViews.push(Plotting.show(figure.figure, `#bokeh-figure-${props.uid}-${index}`));
    }
}

function createPlots() {
    for (const figure of _bokehFigures) {
        figure.lines.length = 0;
        figure.symbols.length = 0;
        figure.figure.renderers.length = 0;
        figure.sources.length = 0;
        figure.legendItems.length = 0;
    }

    const firstCategory = props.categories[0];
    const secondCategory = props.categories[1];

    for (const dataSource of [...props.dataSources].reverse()) {
        const firstElementIndex = firstCategory == null ? null : dataSource[firstCategory.key + 'Index'];
        const secondElementIndex = secondCategory == null ? null : dataSource[secondCategory.key + 'Index'];

        const firstElement = firstCategory == null ? null : _categoryElements.value[0].elements[firstElementIndex];
        const secondElement = secondCategory == null ? null : _categoryElements.value[1].elements[secondElementIndex];

        for (const [plotIndex, plot] of props.plots.entries()) {
            const figure = _bokehFigures[plotIndex];
            let legendLabels = new Set();

            let attrs = {
                visible: dataSource.visible,
                color: firstElement == null ? 'black' : firstElement.color,
                alpha: dataSource.isTopographyAnalysis ? Number(_opacity.value) : dataSource.alpha
            };

            nbPendingAjaxRequests.value++;
            const source = new AjaxDataSource({
                name: dataSource.sourceName,
                data_url: dataSource.url,
                method: "GET",
                content_type: "",
                syncable: false,
                adapter: {
                    execute(obj, cb_data) {
                        if (isMounted.value && nbPendingAjaxRequests.value > 0) {
                            nbPendingAjaxRequests.value--;
                        }

                        const data = cb_data.response;

                        let xData = plot.xData == null ? data.x : plot.xData(data);
                        let yData = plot.yData == null ? data.y : plot.yData(data);

                        if (dataSource.xScaleFactor != null) {
                            xData = xData.map((value) => dataSource.xScaleFactor * value);
                        }
                        if (dataSource.yScaleFactor != null) {
                            yData = yData.map((value) => dataSource.yScaleFactor * value);
                        }

                        let retvals = {
                            x: xData,
                            y: yData
                        };

                        if (plot.auxiliaryDataColumns != null) {
                            for (const [columnName, auxData] of Object.entries(plot.auxiliaryDataColumns)) {
                                retvals[columnName] = data[auxData];
                            }
                        }
                        if (plot.alphaData != null) {
                            retvals['alpha'] = plot.alphaData(data);
                            attrs.alpha = {field: "alpha"};
                        }
                        if (dataSource.subjectName != null) {
                            retvals['subjectName'] = xData.map(() => dataSource.subjectName);
                        }
                        retvals['seriesName'] = xData.map(() => dataSource.seriesName == null ? "-" : dataSource.seriesName);

                        return retvals;
                    }
                }
            });
            figure.sources.unshift(source);

            attrs = {
                ...attrs,
                source: source,
            };

            let renderers = [];

            const line = figure.figure.line(
                {field: "x"},
                {field: "y"},
                {
                    ...attrs,
                    ...{
                        dash: secondElement == null ? 'solid' : secondElement.dash,
                        width: Number(_lineWidth.value) * dataSource.width
                    }
                });
            figure.lines.unshift(line);
            renderers.push(line);

            if (props.showSymbols) {
                const symbolAttrs = {
                    ...attrs,
                    ...{
                        size: Number(_symbolSize.value),
                        visible: dataSource.visible == null || dataSource.visible,
                    }
                };
                let symbols = null;
                if (dataSource.hasParent) {
                    symbols = figure.figure.x(
                        {field: "x"},
                        {field: "y"},
                        symbolAttrs);
                } else {
                    symbols = figure.figure.scatter(
                        {field: "x"},
                        {field: "y"},
                        {...symbolAttrs, marker: "circle"});
                }
                const alphaAttrs = {};
                if (plot.alphaData != null) {
                    alphaAttrs.fill_alpha = {field: "alpha"};
                }
                symbols.selection_glyph = new Scatter({
                    ...alphaAttrs,
                    ...{
                        marker: "circle",
                        size: Number(_symbolSize.value),
                        fill_color: attrs.color,
                        line_color: "black",
                        line_width: 4
                    }
                });
                symbols.nonselection_glyph = new Scatter({
                    ...alphaAttrs,
                    ...{
                        marker: "circle",
                        size: Number(_symbolSize.value),
                        fill_color: attrs.color,
                        line_color: null
                    }
                });
                figure.symbols.unshift(symbols);

                renderers.push(symbols, line);
            }

            let label = legendLabel(dataSource, props.categories);

            if (!legendLabels.has(label)) {
                legendLabels.add(label);
                const item = new LegendItem({
                    label: label,
                    renderers: renderers,
                    visible: dataSource.visible
                });
                figure.legendItems.unshift(item);
                dataSource.legendItem = item;
            }
        }
    }
}

function refreshPlots() {
    for (const [dataSourceIndex, dataSource] of props.dataSources.entries()) {
        for (const figure of _bokehFigures) {
            const line = figure.lines[dataSourceIndex];
            if (line && line.glyph) {
                line.glyph.line_width = Number(_lineWidth.value) * dataSource.width;
                if (dataSource.isTopographyAnalysis) {
                    line.glyph.line_alpha = Number(_opacity.value);
                }
            }

            const symbol = figure.symbols[dataSourceIndex];
            if (symbol && symbol.glyph) {
                symbol.glyph.size = Number(_symbolSize.value);
                if (dataSource.isTopographyAnalysis) {
                    symbol.glyph.line_alpha = Number(_opacity.value);
                    symbol.glyph.fill_alpha = Number(_opacity.value);
                }
            }
        }
    }
}

function setPlotVisibility(categoryIndex, elementIndex, visible) {
    const category = props.categories[categoryIndex];
    const categoryKey = category.key + 'Index';
    for (const [dataSourceIndex, dataSource] of props.dataSources.entries()) {
        if (dataSource[categoryKey] === elementIndex) {
            let dataSourceVisible = visible;
            for (const [i, cat] of props.categories.entries()) {
                if (i !== categoryIndex) {
                    const k = cat.key + 'Index';
                    dataSourceVisible &&= _categoryElementSelections[i][dataSource[k]].value;
                }
            }
            for (const figure of _bokehFigures) {
                if (figure.lines[dataSourceIndex]) figure.lines[dataSourceIndex].visible = dataSourceVisible;
                if (figure.symbols[dataSourceIndex]) figure.symbols[dataSourceIndex].visible = dataSourceVisible;
                if (figure.legendItems[dataSourceIndex]) figure.legendItems[dataSourceIndex].visible = dataSourceVisible;
            }
        }
    }
}

function onTap(obj, data) {
    const name = data.source.name;
    const index = data.source.selected.indices[0];
    for (const bokehPlot of _bokehFigures) {
        for (const source of bokehPlot.sources) {
            if (source.name === name) {
                source.selected.indices = [index];
            }
        }
    }
    emit("selected", obj, data);
}

onBeforeUnmount(() => {
    isMounted.value = false;
    destroyBokehViews();
});

</script>

<template>
    <div class="bokeh-plot-wrapper">
        <div v-if="plots.length === 1" :id="`bokeh-figure-${uid}-0`" class="bokeh-canvas-container"></div>
        <BTabs v-if="plots.length > 1" class="bokeh-tabs mb-2">
            <BTab v-for="(plot, index) in plots"
                  :key="index"
                  :title="plot.title"
                  :active="index === 0">
                <div :id="`bokeh-figure-${uid}-${index}`" class="bokeh-canvas-container"></div>
            </BTab>
        </BTabs>

        <div class="plot-controls mt-2 pt-2 border-top">
            <div class="d-flex flex-wrap align-items-start justify-content-between gap-2 mb-2">
                <!-- Category Filter Clusters -->
                <div class="d-flex flex-column gap-2 flex-grow-1">
                    <div v-for="category in _categoryElements" :key="category.key" class="category-block">
                        <div class="small fw-bold text-secondary mb-1">{{ category.title }}:</div>
                        
                        <div class="d-flex flex-wrap align-items-center gap-2">
                            <div v-for="(group, gIdx) in groupCategoryElements(category.elements)" :key="gIdx"
                                 class="category-group-card d-flex flex-wrap align-items-center gap-1"
                                 :class="{ 'border rounded p-2 bg-light-subtle': group.parent != null }">
                                
                                <!-- Parent / Average Header (if hierarchy exists) -->
                                <div v-if="group.parent"
                                     class="badge rounded-pill cursor-pointer border user-select-none d-flex align-items-center gap-1 transition-all py-1 px-2 me-1"
                                     :class="{ 'bg-primary text-white border-primary': group.parent.selected, 'bg-light text-dark border-secondary-subtle opacity-75': !group.parent.selected }"
                                     @click="toggleGroupParent(group)"
                                     title="Toggle average and all child measurements">
                                    <i class="fa-solid fa-layer-group me-1 small"></i>
                                    <span v-if="group.parent.color != null"
                                          class="dot-indicator" :style="`background-color: #${group.parent.color.toString(16)}`"></span>
                                    <span class="fw-semibold">{{ group.parent.title }}</span>
                                    <span v-if="group.children.length > 0" class="badge bg-secondary-subtle text-dark border ms-1 extra-small">{{ group.children.length }}</span>
                                </div>

                                <!-- Children / Measurement Pills -->
                                <div class="d-flex flex-wrap align-items-center gap-1"
                                     :class="{ 'ps-2 border-start border-2 border-primary-subtle': group.parent != null }">
                                    <div v-for="child in group.children" :key="child.title"
                                         class="badge rounded-pill cursor-pointer border user-select-none d-flex align-items-center gap-1 transition-all py-1 px-2"
                                         :class="{ 'bg-primary text-white border-primary': child.selected, 'bg-light text-dark border-secondary-subtle opacity-75': !child.selected }"
                                         @click="child.selected = !child.selected">
                                        <span v-if="child.color != null"
                                              class="dot-indicator" :style="`background-color: #${child.color.toString(16)}`"></span>
                                        <span>{{ child.title }}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Plot options toggle button -->
                <BButton @click="showOptions = !showOptions" variant="outline-secondary" size="sm" class="ms-auto shadow-none">
                    <i class="fa-solid fa-sliders me-1"></i>
                    {{ showOptions ? 'Hide options' : 'Plot options' }}
                </BButton>
            </div>

            <!-- Expandable Plot Options Panel -->
            <div v-if="showOptions" class="bg-light p-3 rounded border mb-2 shadow-sm transition-all">
                <BokehPlotOptions v-model:layout="_layout"
                                  v-model:legend-location="_legendLocation"
                                  v-model:line-width="_lineWidth"
                                  v-model:symbol-size="_symbolSize"
                                  v-model:opacity="_opacity"
                                  :options-widgets="optionsWidgets">
                </BokehPlotOptions>
            </div>
        </div>
    </div>
</template>

<style scoped>
.dot-indicator {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
}
.cursor-pointer {
    cursor: pointer;
}
.transition-all {
    transition: all 0.2s ease-in-out;
}
.extra-small {
    font-size: 0.7rem;
    padding: 0.15em 0.4em;
}
</style>
