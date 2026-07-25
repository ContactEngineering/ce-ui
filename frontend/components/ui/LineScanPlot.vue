<script setup lang="ts">

import axios from "axios";
import {onBeforeUnmount, onMounted, ref} from "vue";
import {ColumnDataSource, Plotting} from "@bokeh/bokehjs";
import {NetCDFReader} from 'netcdfjs';

import {applyDefaultBokehStyle} from "@/utils/bokeh";
import {maxAbsolute, rescaleLengthUnit} from "@/utils/units";

const props = defineProps({
    topography: Object
});

const _bokehPlotElement = ref(null);

// Bokeh objects, kept so they can be disposed on unmount
let _figure = null;
let _view = null;

onMounted(() => {
    axios.get(props.topography.squeezed_datafile?.file, {responseType: 'arraybuffer'})
        .then(response => {
            const netcdfReader = new NetCDFReader(response.data);
            const x = netcdfReader.getDataVariable('x');
            const heights = netcdfReader.getDataVariable('heights');

            // Position and height are stored in the same unit but routinely
            // differ by orders of magnitude — a scan micrometres long is often
            // only nanometres tall — so each axis gets the unit that suits its
            // own data and reads without an exponent.
            const positionScale = rescaleLengthUnit(maxAbsolute(x), props.topography.unit);
            const heightScale = rescaleLengthUnit(maxAbsolute(heights), props.topography.unit);

            const figure = new Plotting.figure({
                x_axis_label: `Position (${positionScale.unit})`,
                y_axis_label: `Height (${heightScale.unit})`,
                output_backend: 'svg',
                sizing_mode: 'stretch_width'
            });

            // Apply default settings
            applyDefaultBokehStyle(figure);

            // Construct data source
            // `Array.from` rather than `map`, so scaling a typed integer array
            // cannot silently truncate the result back to integers.
            const plot_source = new ColumnDataSource({
                data: {
                    x: Array.from(x, (v: number) => v * positionScale.factor),
                    heights: Array.from(heights, (v: number) => v * heightScale.factor)
                }
            });

            // Construct glyphs
            figure.line({
                x: {field: 'x'},
                y: {field: 'heights'},
                source: plot_source
            });

            // Render to component
            _figure = figure;
            _view = Plotting.show(figure, _bokehPlotElement.value);
        });
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
});

</script>

<template>
    <div ref="_bokehPlotElement"></div>
</template>
