<script setup lang="ts">
/**
 * YAxis - Vertical axis component
 *
 * Renders:
 * - Axis line
 * - Tick marks and labels
 * - Axis label (rotated)
 * - Optional grid lines
 */

import { computed } from 'vue';
import { usePlotContext } from '../core/PlotContext';
import { useAxisTicks } from './useAxisTicks';
import type { AxisConfig } from '../types';

const props = withDefaults(defineProps<{
    /** Axis configuration */
    config?: AxisConfig;
    /** Show grid lines */
    showGrid?: boolean;
    /** Tick length in pixels */
    tickLength?: number;
    /** Gap between tick and label */
    tickLabelGap?: number;
}>(), {
    showGrid: false,
    tickLength: 6,
    tickLabelGap: 4
});

const ctx = usePlotContext();

// Merge config with defaults
const axisConfig = computed<AxisConfig>(() => ({
    scaleType: 'linear',
    ...props.config
}));

// Generate ticks
const { ticks, gridLines } = useAxisTicks({
    scale: ctx.yScaleOriginal,
    config: axisConfig.value,
    orientation: 'y'
});

// Label position (rotated, positioned left of ticks)
const labelX = computed(() => -(props.tickLength + props.tickLabelGap + 35));
</script>

<template>
    <g class="ce-axis ce-y-axis">
        <!-- Grid lines (rendered first, behind axis) -->
        <g v-if="showGrid" class="ce-axis-grid">
            <line
                v-for="position in gridLines"
                :key="`grid-${position}`"
                :x1="0"
                :x2="ctx.dimensions.value.innerWidth"
                :y1="position"
                :y2="position"
                :stroke="ctx.theme.gridColor"
                :stroke-opacity="ctx.theme.gridOpacity"
                stroke-dasharray="2,2"
            />
        </g>

        <!-- Axis line -->
        <line
            class="ce-axis-line"
            x1="0"
            x2="0"
            y1="0"
            :y2="ctx.dimensions.value.innerHeight"
            :stroke="ctx.theme.axisColor"
        />

        <!-- Ticks and labels -->
        <g
            v-for="tick in ticks"
            :key="tick.value"
            class="ce-axis-tick"
            :transform="`translate(0, ${tick.position})`"
        >
            <!-- Tick mark -->
            <line
                :x1="-tickLength"
                x2="0"
                y1="0"
                y2="0"
                :stroke="ctx.theme.axisColor"
            />
            <!-- Tick label -->
            <text
                :x="-(tickLength + tickLabelGap)"
                y="0"
                text-anchor="end"
                dominant-baseline="middle"
                :font-size="ctx.theme.tickFontSize"
                :font-family="ctx.theme.fontFamily"
                :fill="ctx.theme.axisColor"
            >
                {{ tick.label }}
            </text>
        </g>

        <!-- Axis label (rotated) -->
        <text
            v-if="config?.label"
            class="ce-axis-label"
            :transform="`translate(${labelX}, ${ctx.dimensions.value.innerHeight / 2}) rotate(-90)`"
            text-anchor="middle"
            :font-size="ctx.theme.labelFontSize"
            :font-family="ctx.theme.fontFamily"
            :fill="ctx.theme.axisColor"
        >
            {{ config.label }}
        </text>
    </g>
</template>

<style scoped>
.ce-axis-tick text {
    user-select: none;
}

.ce-axis-label {
    font-weight: 500;
}
</style>
