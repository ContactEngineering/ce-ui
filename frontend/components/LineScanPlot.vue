<script setup lang="ts">
/**
 * LineScanPlot - Line plot for 1D topography data
 *
 * Displays a simple line plot for line scan (1D) topography data
 * loaded from a NetCDF file.
 */

import { onMounted, ref, computed } from "vue";
import axios from "axios";
import { NetCDFReader } from 'netcdfjs';

import {
    Plot,
    XAxis,
    YAxis,
    Line
} from "@/lib/ce-plots";
import type { DataSeries, PlotConfig } from "@/lib/ce-plots";

const props = defineProps<{
    topography: {
        squeezed_datafile?: { file: string };
        unit: string;
    };
}>();

const _series = ref<DataSeries[]>([]);
const _loading = ref(true);
const _error = ref<string | null>(null);

const plotConfig = computed<PlotConfig>(() => ({
    xAxis: {
        label: `Position (${props.topography.unit})`,
        type: 'linear'
    },
    yAxis: {
        label: `Height (${props.topography.unit})`,
        type: 'linear'
    }
}));

onMounted(async () => {
    if (!props.topography.squeezed_datafile?.file) {
        _error.value = "No data file available";
        _loading.value = false;
        return;
    }

    try {
        const response = await axios.get(props.topography.squeezed_datafile.file, {
            responseType: 'arraybuffer'
        });

        const netcdfReader = new NetCDFReader(response.data);
        const x = netcdfReader.getDataVariable('x') as number[];
        const heights = netcdfReader.getDataVariable('heights') as number[];

        // Convert to data series
        const points = x.map((xVal, i) => ({
            x: xVal,
            y: heights[i]
        }));

        _series.value = [{
            id: 'line-scan',
            name: 'Height profile',
            data: points,
            visible: true,
            color: '#1f77b4'
        }];
    } catch (e) {
        console.error('Failed to load NetCDF data:', e);
        _error.value = 'Failed to load data';
    } finally {
        _loading.value = false;
    }
});
</script>

<template>
    <div class="line-scan-plot">
        <div v-if="_loading" class="d-flex justify-content-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>

        <div v-else-if="_error" class="alert alert-danger">
            {{ _error }}
        </div>

        <Plot
            v-else-if="_series.length > 0"
            :config="plotConfig"
            :series="_series"
            :aspect-ratio="2"
        >
            <template #axes>
                <XAxis :config="plotConfig.xAxis" :show-grid="true" />
                <YAxis :config="plotConfig.yAxis" :show-grid="true" />
            </template>

            <Line
                v-for="s in _series"
                :key="s.id"
                :series="s"
                :color="s.color"
            />
        </Plot>
    </div>
</template>

<style scoped>
.line-scan-plot {
    width: 100%;
    min-height: 200px;
}
</style>
