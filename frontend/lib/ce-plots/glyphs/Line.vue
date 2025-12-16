<script setup lang="ts">
/**
 * Line - Line glyph component
 *
 * Renders a line connecting data points with support for:
 * - Custom colors
 * - Dash patterns
 * - Line width
 * - Opacity
 * - Visibility toggle
 */

import { computed } from 'vue';
import { line as d3Line, curveLinear } from 'd3-shape';
import { usePlotContext } from '../core/PlotContext';
import type { DataSeries, DashType } from '../types';

const props = withDefaults(defineProps<{
    /** Data series to render */
    series: DataSeries;
    /** Override color from series */
    color?: string;
    /** Override dash pattern from series */
    dash?: DashType;
    /** Override line width from series */
    lineWidth?: number;
    /** Override opacity from series */
    opacity?: number;
}>(), {});

const ctx = usePlotContext();

// Dash pattern mapping
const dashPatterns: Record<DashType, string> = {
    solid: '',
    dashed: '8,4',
    dotted: '2,4',
    dotdash: '8,4,2,4',
    dashdot: '2,4,8,4'
};

// Compute effective styles (props override series properties)
const effectiveColor = computed(() =>
    props.color ?? props.series.color ?? ctx.theme.axisColor
);

const effectiveDash = computed(() =>
    props.dash ?? props.series.dash ?? 'solid'
);

const effectiveLineWidth = computed(() =>
    props.lineWidth ?? props.series.lineWidth ?? ctx.theme.defaultLineWidth
);

const effectiveOpacity = computed(() =>
    props.opacity ?? props.series.opacity ?? ctx.theme.defaultOpacity
);

const dashArray = computed(() => dashPatterns[effectiveDash.value]);

// D3 line generator
const lineGenerator = computed(() => {
    return d3Line<{ x: number; y: number }>()
        .x(d => ctx.xScale.value(d.x))
        .y(d => ctx.yScale.value(d.y))
        .defined(d => isFinite(d.x) && isFinite(d.y) && d.x > 0 && d.y > 0) // Filter invalid points for log scales
        .curve(curveLinear);
});

// Generate path data
const pathD = computed(() => {
    if (props.series.visible === false) return '';
    if (!props.series.data || props.series.data.length === 0) return '';

    const path = lineGenerator.value(props.series.data);
    return path ?? '';
});

// Check if line should be rendered
const shouldRender = computed(() =>
    props.series.visible !== false && pathD.value !== ''
);
</script>

<template>
    <path
        v-if="shouldRender"
        class="ce-line"
        :d="pathD"
        :stroke="effectiveColor"
        :stroke-width="effectiveLineWidth"
        :stroke-dasharray="dashArray"
        :opacity="effectiveOpacity"
        stroke-linecap="round"
        stroke-linejoin="round"
        fill="none"
    />
</template>

<style scoped>
.ce-line {
    pointer-events: none;
}
</style>
