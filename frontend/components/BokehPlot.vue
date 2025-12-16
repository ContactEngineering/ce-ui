<script setup lang="ts">
/**
 * BokehPlot - Multi-series plot with categories and interactive controls
 *
 * A comprehensive plotting component that supports:
 * - Multiple plots in tabs
 * - Categories for grouping/filtering data
 * - AJAX data loading from URLs
 * - Data transformation and scale factors
 * - Configurable line styles, colors, symbols
 * - Legend with visibility toggles
 * - Selection for interactive features
 * - Plot options (layout, legend, line width, symbol size, opacity)
 * - SVG export
 *
 * Migration from Bokeh.js to ce-plots (D3-based).
 */

import { v4 as uuid4 } from 'uuid';
import { computed, onMounted, ref, watch, nextTick } from "vue";

import {
    BAccordion,
    BAccordionItem,
    BFormCheckbox,
    BFormGroup,
    BFormInput,
    BFormSelect,
    BFormSelectOption,
    BTab,
    BTabs
} from "bootstrap-vue-next";

import {
    Plot,
    XAxis,
    YAxis,
    Line,
    Scatter,
    Tooltip,
    Legend,
    useDataLoader,
    useTooltip,
    useSelection,
    useExport,
    PLASMA_256,
    GREYS_256,
    getColorByValue,
    formatExponential
} from "@/lib/ce-plots";
import type { DataSeries, DataPoint, PlotConfig, TooltipContext } from "@/lib/ce-plots";

// Bookkeeping of pending ajax requests for displaying spinners
const nbPendingAjaxRequests = defineModel('nbPendingAjaxRequests', { required: false, default: 0 });

// Emitted when a dataset is selected
const emit = defineEmits(['selected']);

interface Category {
    key: string;
    title: string;
}

interface PlotDefinition {
    title: string;
    xData?: (data: any) => number[];
    yData?: (data: any) => number[];
    auxiliaryDataColumns?: Record<string, string>;
    alphaData?: (data: any) => number[];
    xAxisType?: 'linear' | 'log';
    yAxisType?: 'linear' | 'log';
    xAxisLabel?: string;
    yAxisLabel?: string;
}

interface DataSourceDefinition {
    url: string;
    sourceName?: string;
    legendLabel?: string;
    subjectName?: string;
    seriesName?: string;
    hasParent?: boolean;
    visible?: boolean;
    width?: number;
    alpha?: number;
    isTopographyAnalysis?: boolean;
    xScaleFactor?: number;
    yScaleFactor?: number;
    [key: string]: any; // Category keys
}

const props = withDefaults(defineProps<{
    categories?: Category[];
    plots?: PlotDefinition[];
    dataSources?: DataSourceDefinition[];
    outputBackend?: string;
    height?: number;
    width?: number | null;
    showSymbols?: boolean;
    sizingMode?: string;
    aspectRatio?: number;
    uid?: string;
    selectable?: boolean;
    optionsWidgets?: string[];
    functionTitle?: string;
}>(), {
    categories: () => [],
    plots: () => [{
        title: "default",
        xData: undefined,
        yData: undefined,
        auxiliaryDataColumns: undefined,
        alphaData: undefined,
        xAxisType: "linear",
        yAxisType: "linear",
        xAxisLabel: "x",
        yAxisLabel: "y"
    }],
    dataSources: () => [],
    outputBackend: 'svg',
    height: 300,
    width: null,
    showSymbols: true,
    sizingMode: "scale_width",
    aspectRatio: 2,
    uid: () => uuid4(),
    selectable: false,
    optionsWidgets: () => ["layout", "legend", "lineWidth", "symbolSize", "opacity"],
    functionTitle: "bokeh_plot"
});

// GUI logic
const _layout = ref("web");
const _legendLocation = ref("off");
const _symbolSize = ref(10);
const _opacity = ref(0.4);
const _lineWidth = ref(1);
const _activeTab = ref(0);

// Color palettes
const _parentColorPalette = GREYS_256;
const _childColorPalette = PLASMA_256;
const _dashes: Array<'solid' | 'dashed' | 'dotted' | 'dashdot'> = ['solid', 'dashed', 'dotted', 'dashdot'];

// Data loader
const { loading, loadRaw } = useDataLoader();

// Tooltip
const { visible: tooltipVisible, context: tooltipContext, position: tooltipPosition, show: showTooltip, hide: hideTooltip, updatePosition } = useTooltip();

// Selection
const { selection, hasSelection, select, clear: clearSelection, isSelected } = useSelection({
    onSelect: (sel) => {
        if (sel && !Array.isArray(sel)) {
            emit('selected', null, {
                source: {
                    name: sel.seriesId,
                    selected: { indices: [sel.pointIndex] },
                    data: _loadedDataBySeriesId.value[sel.seriesId!] || {}
                }
            });
        }
    }
});

// Export
const _plotRefs = ref<Array<{ svgElement: SVGElement | null }>>([]);
const { exportSvg } = useExport({ defaultFilename: props.functionTitle.replace(" ", "_").toLowerCase() });

// Loaded data storage
const _loadedData = ref<Map<string, any>>(new Map());
const _loadedDataBySeriesId = ref<Record<string, any>>({});

// Category elements for UI
const _categoryElements = ref<Array<{
    key: string;
    title: string;
    elements: Array<{
        title: string;
        color: string;
        dash: string;
        hasParent: boolean;
        selected: boolean;
    }>;
}>>([]);

// Internal visibility state
const _visibilityState = ref<Map<string, boolean>>(new Map());

// Computed series for each plot
const _plotSeries = ref<Array<DataSeries[]>>([]);

// Initialize on mount
onMounted(async () => {
    if (props.dataSources.length > 0) {
        await updateCategoryElements();
        await loadAllData();
    }
});

// Watch for data source changes
watch(() => props.dataSources, async (newVal, oldVal) => {
    let hasChanged = newVal.length !== oldVal.length;
    if (!hasChanged) {
        for (const [index, val] of newVal.entries()) {
            hasChanged = hasChanged || (val.url !== oldVal[index]?.url);
        }
    }
    if (hasChanged) {
        await updateCategoryElements();
        await loadAllData();
    }
}, { deep: true });

// Watch layout changes
watch(_layout, (layout) => {
    switch (layout) {
        case 'web':
            _symbolSize.value = 10;
            break;
        case 'print-single':
        case 'print-double':
            _symbolSize.value = 5;
            break;
    }
});

function legendLabel(dataSource: DataSourceDefinition): string {
    let label = dataSource.sourceName || '';
    if (dataSource.legendLabel != null) {
        label = dataSource.legendLabel;
    } else if (props.categories.length > 0) {
        label = dataSource[props.categories[0].key];
        if (dataSource.hasParent === true) {
            label = "└─ " + label;
        }
    }
    return label;
}

async function updateCategoryElements() {
    _categoryElements.value = [];
    _visibilityState.value.clear();

    // For each category, create a list of unique entries
    for (const [categoryIndex, category] of props.categories.entries()) {
        const elements: Array<{
            title: string;
            color: string;
            dash: string;
            hasParent: boolean;
            selected: boolean;
        }> = [];

        const seenIndices = new Set<number>();

        for (const dataSource of props.dataSources) {
            if (!(category.key in dataSource)) {
                throw new Error(`Key '${category.key}' not found in data source.`);
            }

            const title = dataSource[category.key];
            const elementIndex = dataSource[category.key + 'Index'] ?? 0;
            const hasParent = dataSource[category.key + 'HasParent'] ?? false;

            if (seenIndices.has(elementIndex)) continue;
            seenIndices.add(elementIndex);

            // Defaults to showing a data source if it has no 'visible' attribute
            const visible = dataSource.visible == null || dataSource.visible;
            _visibilityState.value.set(`${categoryIndex}-${elementIndex}`, visible);

            elements[elementIndex] = {
                title,
                color: '',
                dash: 'solid',
                hasParent,
                selected: visible
            };
        }

        _categoryElements.value.push({
            key: category.key,
            title: category.title,
            elements: elements.filter(e => e !== undefined)
        });
    }

    // Assign colors to first category
    if (_categoryElements.value.length > 0) {
        let nbParents = 0;
        let nbChildren = 0;
        for (const element of _categoryElements.value[0].elements) {
            if (element.hasParent) {
                nbChildren++;
            } else {
                nbParents++;
            }
        }

        let parentIndex = 0;
        let childIndex = 0;
        for (const element of _categoryElements.value[0].elements) {
            if (element.hasParent) {
                element.color = getColorByValue(_childColorPalette, childIndex / Math.max(1, nbChildren - 1));
                childIndex++;
            } else {
                if (nbChildren === 0) {
                    element.color = getColorByValue(_childColorPalette, parentIndex / Math.max(1, nbParents - 1));
                } else {
                    element.color = getColorByValue(_parentColorPalette, parentIndex / Math.max(1, nbParents - 1));
                }
                parentIndex++;
            }
        }

        // Assign dash patterns to second category
        if (_categoryElements.value[1]) {
            for (let [elementIndex, element] of _categoryElements.value[1].elements.entries()) {
                element.dash = _dashes[elementIndex % _dashes.length];
            }
        }
    }
}

async function loadAllData() {
    _loadedData.value.clear();
    _loadedDataBySeriesId.value = {};
    const plotSeriesArray: DataSeries[][] = props.plots.map(() => []);

    for (const [dsIndex, dataSource] of props.dataSources.entries()) {
        try {
            nbPendingAjaxRequests.value++;
            const rawData = await loadRaw(dataSource.url);
            _loadedData.value.set(dataSource.url, rawData);

            // Get category element info
            const firstCategory = props.categories[0];
            const secondCategory = props.categories[1];
            const firstElementIndex = firstCategory ? (dataSource[firstCategory.key + 'Index'] ?? 0) : 0;
            const secondElementIndex = secondCategory ? (dataSource[secondCategory.key + 'Index'] ?? 0) : 0;
            const firstElement = _categoryElements.value[0]?.elements[firstElementIndex];
            const secondElement = _categoryElements.value[1]?.elements[secondElementIndex];

            // Create series for each plot
            for (const [plotIndex, plot] of props.plots.entries()) {
                let xData = plot.xData ? plot.xData(rawData) : rawData.x;
                let yData = plot.yData ? plot.yData(rawData) : rawData.y;

                // Apply scale factors
                if (dataSource.xScaleFactor != null) {
                    xData = xData.map((v: number) => v * dataSource.xScaleFactor!);
                }
                if (dataSource.yScaleFactor != null) {
                    yData = yData.map((v: number) => v * dataSource.yScaleFactor!);
                }

                // Build points
                const points: DataPoint[] = xData.map((x: number, i: number) => {
                    const point: DataPoint = { x, y: yData[i] };

                    // Add auxiliary columns
                    if (plot.auxiliaryDataColumns) {
                        for (const [colName, dataKey] of Object.entries(plot.auxiliaryDataColumns)) {
                            point[colName] = rawData[dataKey]?.[i];
                        }
                    }

                    // Add alpha
                    if (plot.alphaData) {
                        point.alpha = plot.alphaData(rawData)[i];
                    }

                    // Add metadata
                    point.subjectName = dataSource.subjectName;
                    point.seriesName = dataSource.seriesName || '-';

                    return point;
                });

                const seriesId = `ds-${dsIndex}-plot-${plotIndex}`;
                const series: DataSeries = {
                    id: seriesId,
                    name: legendLabel(dataSource),
                    data: points,
                    visible: dataSource.visible !== false,
                    color: firstElement?.color || '#333',
                    dash: (secondElement?.dash || 'solid') as any,
                    symbol: dataSource.hasParent ? 'x' : 'circle'
                };

                plotSeriesArray[plotIndex].push(series);

                // Store for selection callback
                _loadedDataBySeriesId.value[seriesId] = rawData;
            }
        } catch (e) {
            console.error(`Failed to load data from ${dataSource.url}:`, e);
        } finally {
            nbPendingAjaxRequests.value--;
        }
    }

    _plotSeries.value = plotSeriesArray;
}

function toggleCategoryElement(categoryIndex: number, elementIndex: number, selected: boolean) {
    const key = `${categoryIndex}-${elementIndex}`;
    _visibilityState.value.set(key, selected);

    // Update element state
    if (_categoryElements.value[categoryIndex]?.elements[elementIndex]) {
        _categoryElements.value[categoryIndex].elements[elementIndex].selected = selected;
    }

    // Update series visibility
    updateSeriesVisibility();
}

function updateSeriesVisibility() {
    const category = props.categories[0];
    if (!category) return;

    for (const [plotIndex, series] of _plotSeries.value.entries()) {
        for (const [seriesIndex, s] of series.entries()) {
            const dsIndex = parseInt(s.id.split('-')[1]);
            const dataSource = props.dataSources[dsIndex];
            if (!dataSource) continue;

            let visible = true;
            for (const [catIndex, cat] of props.categories.entries()) {
                const elemIndex = dataSource[cat.key + 'Index'] ?? 0;
                const key = `${catIndex}-${elemIndex}`;
                visible = visible && (_visibilityState.value.get(key) !== false);
            }

            s.visible = visible;
        }
    }

    // Trigger reactivity
    _plotSeries.value = [..._plotSeries.value];
}

function handleHover(context: TooltipContext | null, event?: MouseEvent) {
    if (context && event) {
        updatePosition(event.clientX, event.clientY);
        showTooltip(context);
    } else {
        hideTooltip();
    }
}

function handleClick(seriesId: string, pointIndex: number) {
    if (props.selectable) {
        select(seriesId, pointIndex);
    }
}

function download() {
    const plotRef = _plotRefs.value[_activeTab.value];
    if (plotRef?.svgElement) {
        exportSvg(plotRef.svgElement);
    }
}

// Computed plot configs
const plotConfigs = computed(() => {
    return props.plots.map(plot => ({
        xAxis: {
            label: plot.xAxisLabel || 'x',
            scaleType: plot.xAxisType || 'linear'
        },
        yAxis: {
            label: plot.yAxisLabel || 'y',
            scaleType: plot.yAxisType || 'linear'
        }
    } as PlotConfig));
});

// Get effective opacity for a series
function getSeriesOpacity(dsIndex: number): number {
    const dataSource = props.dataSources[dsIndex];
    if (dataSource?.isTopographyAnalysis) {
        return Number(_opacity.value);
    }
    return dataSource?.alpha ?? 1;
}

// Get effective line width
function getSeriesLineWidth(dsIndex: number): number {
    const dataSource = props.dataSources[dsIndex];
    const width = dataSource?.width ?? 1;
    return Number(_lineWidth.value) * width;
}

// Legend visibility
const showLegend = computed(() => _legendLocation.value !== 'off');

// Expose download method for parent components
defineExpose({ download });
</script>

<template>
    <div class="ce-plot-container">
        <!-- Single plot -->
        <div v-if="plots.length === 1 && _plotSeries[0]">
            <Plot
                ref="_plotRefs[0]"
                :config="plotConfigs[0]"
                :series="_plotSeries[0]"
                :height="height"
                :aspect-ratio="aspectRatio"
            >
                <template #axes>
                    <XAxis
                        :config="plotConfigs[0].xAxis"
                        :show-grid="true"
                        :format-tick="plotConfigs[0].xAxis.scaleType === 'linear' ? formatExponential : undefined"
                    />
                    <YAxis
                        :config="plotConfigs[0].yAxis"
                        :show-grid="true"
                        :format-tick="plotConfigs[0].yAxis.scaleType === 'linear' ? formatExponential : undefined"
                    />
                </template>

                <template v-for="(series, idx) in _plotSeries[0]" :key="series.id">
                    <Line
                        v-if="series.visible"
                        :series="series"
                        :color="series.color"
                        :dash="series.dash"
                        :stroke-width="getSeriesLineWidth(parseInt(series.id.split('-')[1]))"
                        :opacity="getSeriesOpacity(parseInt(series.id.split('-')[1]))"
                    />
                    <Scatter
                        v-if="series.visible && showSymbols"
                        :series="series"
                        :color="series.color"
                        :symbol="series.symbol || 'circle'"
                        :size="_symbolSize"
                        :opacity="getSeriesOpacity(parseInt(series.id.split('-')[1]))"
                        :selectable="selectable"
                        @hover="handleHover"
                        @click="handleClick"
                    />
                </template>
            </Plot>
        </div>

        <!-- Multiple plots in tabs -->
        <BTabs v-if="plots.length > 1" v-model="_activeTab">
            <BTab
                v-for="(plot, plotIndex) in plots"
                :key="plotIndex"
                :title="plot.title"
            >
                <Plot
                    v-if="_plotSeries[plotIndex]"
                    :ref="el => _plotRefs[plotIndex] = el"
                    :config="plotConfigs[plotIndex]"
                    :series="_plotSeries[plotIndex]"
                    :height="height"
                    :aspect-ratio="aspectRatio"
                >
                    <template #axes>
                        <XAxis
                            :config="plotConfigs[plotIndex].xAxis"
                            :show-grid="true"
                            :format-tick="plotConfigs[plotIndex].xAxis.scaleType === 'linear' ? formatExponential : undefined"
                        />
                        <YAxis
                            :config="plotConfigs[plotIndex].yAxis"
                            :show-grid="true"
                            :format-tick="plotConfigs[plotIndex].yAxis.scaleType === 'linear' ? formatExponential : undefined"
                        />
                    </template>

                    <template v-for="(series, idx) in _plotSeries[plotIndex]" :key="series.id">
                        <Line
                            v-if="series.visible"
                            :series="series"
                            :color="series.color"
                            :dash="series.dash"
                            :stroke-width="getSeriesLineWidth(parseInt(series.id.split('-')[1]))"
                            :opacity="getSeriesOpacity(parseInt(series.id.split('-')[1]))"
                        />
                        <Scatter
                            v-if="series.visible && showSymbols"
                            :series="series"
                            :color="series.color"
                            :symbol="series.symbol || 'circle'"
                            :size="_symbolSize"
                            :opacity="getSeriesOpacity(parseInt(series.id.split('-')[1]))"
                            :selectable="selectable"
                            @hover="handleHover"
                            @click="handleClick"
                        />
                    </template>
                </Plot>
            </BTab>
        </BTabs>

        <!-- Legend -->
        <div v-if="showLegend && _plotSeries[_activeTab]?.length > 0" class="ce-plot-legend mt-2">
            <Legend
                :series="_plotSeries[_activeTab]"
                :position="_legendLocation"
                :show-checkboxes="false"
                orientation="vertical"
            />
        </div>

        <!-- Tooltip -->
        <Tooltip
            :visible="tooltipVisible"
            :context="tooltipContext"
            :position="tooltipPosition"
            :format-value="formatExponential"
        />

        <!-- Category accordions and options -->
        <BAccordion class="mt-3">
            <BAccordionItem
                v-for="(category, categoryIndex) in _categoryElements"
                :key="category.key"
                :title="category.title"
            >
                <BFormCheckbox
                    v-for="(element, elementIndex) in category.elements"
                    :key="elementIndex"
                    :model-value="element.selected"
                    @update:model-value="val => toggleCategoryElement(categoryIndex, elementIndex, val)"
                >
                    <span
                        v-if="element.color"
                        class="color-dot"
                        :style="{ backgroundColor: element.color }"
                    ></span>
                    <span v-if="element.hasParent">└─</span>
                    {{ element.title }}
                </BFormCheckbox>
            </BAccordionItem>

            <BAccordionItem title="Plot options">
                <BFormGroup
                    v-if="optionsWidgets.includes('layout')"
                    class="mt-2"
                    label="Plot layout"
                    label-cols="4"
                    content-cols="8"
                >
                    <BFormSelect v-model="_layout">
                        <BFormSelectOption value="web">
                            Optimize plot for web (plot scales with window size)
                        </BFormSelectOption>
                        <BFormSelectOption value="print-single">
                            Optimize plot for print (single-column layout)
                        </BFormSelectOption>
                        <BFormSelectOption value="print-double">
                            Optimize plot for print (two-column layout)
                        </BFormSelectOption>
                    </BFormSelect>
                </BFormGroup>

                <BFormGroup
                    v-if="optionsWidgets.includes('legend')"
                    class="mt-2"
                    label="Legend"
                    label-cols="4"
                    content-cols="8"
                >
                    <BFormSelect v-model="_legendLocation">
                        <BFormSelectOption value="off">Do not show legend</BFormSelectOption>
                        <BFormSelectOption value="top_right">Show legend top right</BFormSelectOption>
                        <BFormSelectOption value="top_left">Show legend top left</BFormSelectOption>
                        <BFormSelectOption value="bottom_right">Show legend bottom right</BFormSelectOption>
                        <BFormSelectOption value="bottom_left">Show legend bottom left</BFormSelectOption>
                    </BFormSelect>
                </BFormGroup>

                <BFormGroup
                    v-if="optionsWidgets.includes('lineWidth')"
                    class="mt-2"
                    label="Line width"
                    label-cols="4"
                    content-cols="8"
                >
                    <BFormInput
                        type="range"
                        min="0.1"
                        max="3.0"
                        step="0.1"
                        v-model="_lineWidth"
                    />
                </BFormGroup>

                <BFormGroup
                    v-if="optionsWidgets.includes('symbolSize')"
                    class="mt-2"
                    label="Symbol size"
                    label-cols="4"
                    content-cols="8"
                >
                    <BFormInput
                        type="range"
                        min="1"
                        max="20"
                        step="1"
                        v-model="_symbolSize"
                    />
                </BFormGroup>

                <BFormGroup
                    v-if="optionsWidgets.includes('opacity')"
                    class="mt-2"
                    label="Opacity of lines/symbols (measurements only)"
                    label-cols="4"
                    content-cols="8"
                >
                    <BFormInput
                        type="range"
                        min="0"
                        max="1"
                        step="0.1"
                        v-model="_opacity"
                    />
                </BFormGroup>
            </BAccordionItem>
        </BAccordion>
    </div>
</template>

<style scoped>
.ce-plot-container {
    width: 100%;
}

.ce-plot-legend {
    display: flex;
    justify-content: flex-end;
}

.color-dot {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 2px;
    margin-right: 6px;
    vertical-align: middle;
}
</style>
