<script setup>

import {onBeforeUnmount, onMounted, ref, watch} from "vue";
import {ColumnDataSource, HoverTool, OpenURL, Plotting, TapTool} from "@bokeh/bokehjs";
import {applyDefaultBokehStyle} from "../utils/bokeh";

const props = defineProps({
    topographies: {
        type: Object,
        default: []
    }
});

const _bokehPlotElement = ref(null);

// Bokeh objects, kept so they can be disposed on unmount
let _figure = null;
let _view = null;

// Hover tool
const hover_tool = new HoverTool({
    'tooltips': '<div style="width: 7rem;">' +
        '<img src="@thumbnail" width="100%" alt="Thumbnail is missing">' +
        '<span>@name</span>' +
        '</div>'
});

// Tap tool
const tap_tool = new TapTool({
    callback: new OpenURL({
        url: "@link",
        same_tab: true
    })
});

// Construct data source
const bw_source = new ColumnDataSource({
    data: {
        y: [],
        left: [],
        cutoff: [],
        right: [],
        name: [],
        thumbnail: [],
        link: []
    }
});

function setPlotData(topographies) {
    // Filter nulls
    const filtered_topographies = topographies.filter(t => t !== null);

    // Sort topographies
    const left = filtered_topographies.map(t => t.bandwidth_lower);
    const argsort = left.map((v, i) => [v, i]).sort((a, b) => a[0] - b[0]).map(a => a[1]);
    let y = Array(argsort.length);
    for (const i of argsort.keys()) {
        y[argsort[i]] = i;
    }

    // Construct data source
    bw_source.data = {
        y: y,
        left: left,
        cutoff: filtered_topographies.map(t => t.short_reliability_cutoff),
        right: filtered_topographies.map(t => t.bandwidth_upper),
        name: filtered_topographies.map(t => t.name),
        thumbnail: filtered_topographies.map(t => t.thumbnail == null ? null : t.thumbnail.file),
        link: filtered_topographies.map(t => `/ui/topography/${t.id}/`),
    };
}

onMounted(() => {
    // Bokeh figure
    const figure = new Plotting.Figure({
        x_axis_label: 'Bandwidth (m)',
        x_axis_type: 'log',
        output_backend: 'svg',
        sizing_mode: 'stretch_width',
        tools: [hover_tool, tap_tool],
        toolbar_location: null,
    });

    // Apply default settings
    applyDefaultBokehStyle(figure);

    // Adjust properties not accessible in the constructor
    figure.yaxis.visible = false;
    figure.grid.visible = false;
    figure.outline_line_color = null;
    figure.legend.location = "top_left";
    figure.legend.title = "Measurement artifacts";
    figure.legend.title_text_font_style = "bold";
    figure.legend.background_fill_color = "#f0f0f0";
    figure.legend.border_line_width = 3;
    figure.legend.border_line_cap = "round";

    // Construct glyphs
    figure.hbar({
        y: {field: 'y'},
        left: {field: 'left'},
        right: {field: 'right'},
        height: 1.0,
        color: '#2c90d9',
        name: 'bandwidths',
        legend_label: "Reliable",
        level: "underlay",
        source: bw_source
    });

    figure.hbar({
        y: {field: 'y'},
        left: {field: 'left'},
        right: {field: 'cutoff'},
        height: 1.0,
        color: '#dc3545',
        name: 'bandwidths',
        legend_label: "Unreliable",
        level: "underlay",
        source: bw_source
    });

    // Render to component
    _figure = figure;
    _view = Plotting.show(figure, _bokehPlotElement.value);

    // Set data
    setPlotData(props.topographies);
});

watch(() => props.topographies, (newValue, oldValue) => {
    setPlotData(newValue);
});

onBeforeUnmount(() => {
    /* Dispose the embedded Bokeh view and clear the figure's document so they do not leak. */
    if (_view != null) {
        Promise.resolve(_view).then(view => {
            try {
                if (view != null && typeof view.remove === "function") {
                    view.remove();
                }
            } catch (e) {
                /* Ignore errors during teardown */
            }
        }).catch(() => { /* Ignore rejected view promises during teardown */ });
        _view = null;
    }
    try {
        const doc = _figure == null ? null : _figure.document;
        if (doc != null && typeof doc.clear === "function") {
            doc.clear();
        }
    } catch (e) {
        /* Ignore errors during teardown */
    }
    _figure = null;
    // Clear the data source accumulators
    bw_source.data = {
        y: [], left: [], cutoff: [], right: [], name: [], thumbnail: [], link: []
    };
});

</script>

<template>
    <div ref="_bokehPlotElement"></div>
</template>
