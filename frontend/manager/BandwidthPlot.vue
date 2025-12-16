<script setup lang="ts">
/**
 * BandwidthPlot - Horizontal bar plot showing measurement bandwidths
 *
 * Displays bandwidth ranges for topographies as horizontal bars.
 * Features:
 * - Reliable vs unreliable regions (based on short reliability cutoff)
 * - Hover tooltips with thumbnail images
 * - Click to navigate to topography detail
 */

import { computed, ref, watch } from "vue";

import {
    Plot,
    XAxis,
    HBar,
    Tooltip,
    useTooltip,
    Legend
} from "@/lib/ce-plots";
import type { PlotConfig, TooltipContext, DataSeries } from "@/lib/ce-plots";

interface Topography {
    id: number;
    name: string;
    bandwidth_lower: number;
    bandwidth_upper: number;
    short_reliability_cutoff: number | null;
    thumbnail?: { file: string } | null;
}

const props = defineProps<{
    topographies: Topography[];
}>();

const { tooltipVisible, tooltipContext, tooltipPosition, showTooltip, hideTooltip, updatePosition } = useTooltip();

// Current hover state for custom tooltip
const _hoverData = ref<{
    name: string;
    thumbnail: string | null;
} | null>(null);

const plotConfig = computed<PlotConfig>(() => ({
    xAxis: {
        label: 'Bandwidth (m)',
        type: 'log'
    },
    yAxis: {
        label: '',
        type: 'linear'
    }
}));

// Process topographies into bar data
const processedData = computed(() => {
    // Filter nulls
    const filtered = props.topographies.filter(t => t !== null);

    // Sort by bandwidth_lower
    const sorted = [...filtered].sort((a, b) => a.bandwidth_lower - b.bandwidth_lower);

    // Build bar data for reliable regions
    const reliableBars = sorted.map((t, i) => ({
        y: i,
        left: t.bandwidth_lower,
        right: t.bandwidth_upper,
        name: t.name,
        thumbnail: t.thumbnail?.file ?? null,
        link: `/ui/topography/${t.id}/`,
        topographyId: t.id
    }));

    // Build bar data for unreliable regions (up to short_reliability_cutoff)
    const unreliableBars = sorted
        .filter(t => t.short_reliability_cutoff !== null)
        .map((t, i) => {
            const originalIndex = sorted.findIndex(s => s.id === t.id);
            return {
                y: originalIndex,
                left: t.bandwidth_lower,
                right: t.short_reliability_cutoff!,
                name: t.name,
                thumbnail: t.thumbnail?.file ?? null,
                link: `/ui/topography/${t.id}/`,
                topographyId: t.id
            };
        });

    return { reliableBars, unreliableBars, count: sorted.length };
});

// Convert to series for HBar
const reliableSeries = computed<DataSeries>(() => ({
    id: 'reliable',
    name: 'Reliable',
    data: processedData.value.reliableBars.map(bar => ({
        x: bar.left,
        y: bar.y,
        left: bar.left,
        right: bar.right,
        name: bar.name,
        thumbnail: bar.thumbnail,
        link: bar.link,
        topographyId: bar.topographyId
    })),
    visible: true,
    color: '#2c90d9'
}));

const unreliableSeries = computed<DataSeries>(() => ({
    id: 'unreliable',
    name: 'Unreliable',
    data: processedData.value.unreliableBars.map(bar => ({
        x: bar.left,
        y: bar.y,
        left: bar.left,
        right: bar.right,
        name: bar.name,
        thumbnail: bar.thumbnail,
        link: bar.link,
        topographyId: bar.topographyId
    })),
    visible: true,
    color: '#dc3545'
}));

const legendSeries = computed(() => [
    { id: 'reliable', name: 'Reliable', color: '#2c90d9', visible: true, data: [] },
    { id: 'unreliable', name: 'Unreliable', color: '#dc3545', visible: true, data: [] }
]);

function handleHover(context: TooltipContext | null, event?: MouseEvent) {
    if (context && event) {
        _hoverData.value = {
            name: context.point.name as string,
            thumbnail: context.point.thumbnail as string | null
        };
        updatePosition(event.clientX, event.clientY);
        showTooltip(context);
    } else {
        _hoverData.value = null;
        hideTooltip();
    }
}

function handleClick(seriesId: string, pointIndex: number, point: any) {
    if (point.link) {
        window.location.href = point.link;
    }
}
</script>

<template>
    <div class="bandwidth-plot">
        <Plot
            v-if="processedData.count > 0"
            :config="plotConfig"
            :series="[reliableSeries, unreliableSeries]"
            :aspect-ratio="Math.max(1.5, processedData.count * 0.3)"
            :margins="{ top: 20, right: 20, bottom: 50, left: 20 }"
        >
            <template #axes>
                <XAxis :config="plotConfig.xAxis" />
            </template>

            <!-- Reliable bars (full bandwidth) - rendered first (underneath) -->
            <HBar
                :series="reliableSeries"
                :height="0.8"
                :color="reliableSeries.color"
                @hover="handleHover"
                @click="handleClick"
            />

            <!-- Unreliable bars (partial, up to cutoff) - rendered on top -->
            <HBar
                :series="unreliableSeries"
                :height="0.8"
                :color="unreliableSeries.color"
                @hover="handleHover"
                @click="handleClick"
            />
        </Plot>

        <!-- Legend -->
        <div v-if="processedData.count > 0" class="bandwidth-legend mt-2">
            <Legend
                :series="legendSeries"
                :show-checkboxes="false"
                position="bottom"
                orientation="horizontal"
            />
        </div>

        <!-- Custom tooltip with thumbnail -->
        <Teleport to="body">
            <div
                v-if="tooltipVisible && _hoverData"
                class="bandwidth-tooltip"
                :style="{
                    left: `${tooltipPosition.x + 12}px`,
                    top: `${tooltipPosition.y + 12}px`
                }"
            >
                <img
                    v-if="_hoverData.thumbnail"
                    :src="_hoverData.thumbnail"
                    alt="Thumbnail"
                    class="bandwidth-tooltip-image"
                />
                <span class="bandwidth-tooltip-name">{{ _hoverData.name }}</span>
            </div>
        </Teleport>
    </div>
</template>

<style scoped>
.bandwidth-plot {
    width: 100%;
}

.bandwidth-legend {
    display: flex;
    justify-content: center;
}

.bandwidth-tooltip {
    position: fixed;
    z-index: 1000;
    pointer-events: none;
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    padding: 8px;
    max-width: 150px;
}

.bandwidth-tooltip-image {
    width: 100%;
    margin-bottom: 6px;
    border-radius: 2px;
}

.bandwidth-tooltip-name {
    display: block;
    font-size: 12px;
    color: #333;
    word-wrap: break-word;
}
</style>
