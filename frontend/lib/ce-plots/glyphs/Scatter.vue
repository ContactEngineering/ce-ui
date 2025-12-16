<script setup lang="ts">
/**
 * Scatter - Scatter plot glyph component
 *
 * Renders data points as symbols with support for:
 * - Multiple symbol types (circle, x, square, triangle, diamond)
 * - Custom colors
 * - Symbol size
 * - Opacity
 * - Selection highlighting
 * - Hover and click events
 */

import { computed } from 'vue';
import {
    symbol as d3Symbol,
    symbolCircle,
    symbolCross,
    symbolSquare,
    symbolTriangle,
    symbolDiamond
} from 'd3-shape';
import { usePlotContext } from '../core/PlotContext';
import type { DataSeries, SymbolType, DataPoint } from '../types';

const props = withDefaults(defineProps<{
    /** Data series to render */
    series: DataSeries;
    /** Override color from series */
    color?: string;
    /** Override symbol type from series */
    symbol?: SymbolType;
    /** Override symbol size from series */
    symbolSize?: number;
    /** Override opacity from series */
    opacity?: number;
    /** Enable click selection */
    selectable?: boolean;
    /** Enable hover effects */
    hoverable?: boolean;
}>(), {
    selectable: false,
    hoverable: true
});

const emit = defineEmits<{
    /** Emitted when a point is clicked */
    (e: 'pointClick', index: number, point: DataPoint): void;
    /** Emitted when mouse enters a point */
    (e: 'pointEnter', index: number, point: DataPoint, event: MouseEvent): void;
    /** Emitted when mouse leaves a point */
    (e: 'pointLeave', index: number, point: DataPoint, event: MouseEvent): void;
}>();

const ctx = usePlotContext();

// Symbol type mapping
const symbolTypes: Record<SymbolType, any> = {
    circle: symbolCircle,
    x: symbolCross,
    square: symbolSquare,
    triangle: symbolTriangle,
    diamond: symbolDiamond
};

// Compute effective styles
const effectiveColor = computed(() =>
    props.color ?? props.series.color ?? ctx.theme.axisColor
);

const effectiveSymbol = computed(() =>
    props.symbol ?? props.series.symbol ?? 'circle'
);

const effectiveSize = computed(() =>
    props.symbolSize ?? props.series.symbolSize ?? ctx.theme.defaultSymbolSize
);

const effectiveOpacity = computed(() =>
    props.opacity ?? props.series.opacity ?? ctx.theme.defaultOpacity
);

// Generate symbol path
const symbolPath = computed(() => {
    const symbolType = symbolTypes[effectiveSymbol.value];
    // D3 symbol size is area, so we square the pixel size
    const area = Math.pow(effectiveSize.value, 2);
    return d3Symbol().type(symbolType).size(area)() ?? '';
});

// Transform data points to screen coordinates
const points = computed(() => {
    if (props.series.visible === false) return [];
    if (!props.series.data || props.series.data.length === 0) return [];

    return props.series.data
        .map((d, index) => {
            const x = ctx.xScale.value(d.x);
            const y = ctx.yScale.value(d.y);

            // Filter out invalid points (NaN, Infinity, or out of log scale range)
            if (!isFinite(x) || !isFinite(y)) return null;

            return {
                index,
                x,
                y,
                data: d
            };
        })
        .filter((p): p is NonNullable<typeof p> => p !== null);
});

// Check if a point is selected
function isSelected(index: number): boolean {
    return ctx.selection.value.seriesId === props.series.id &&
           ctx.selection.value.pointIndex === index;
}

// Event handlers
function handleClick(index: number, point: DataPoint) {
    if (props.selectable) {
        ctx.selectPoint(props.series.id, index);
    }
    emit('pointClick', index, point);
}

function handleMouseEnter(index: number, point: DataPoint, event: MouseEvent) {
    if (props.hoverable) {
        ctx.showTooltip({
            point,
            series: props.series,
            screenX: event.clientX,
            screenY: event.clientY
        });
    }
    emit('pointEnter', index, point, event);
}

function handleMouseMove(event: MouseEvent) {
    if (props.hoverable) {
        ctx.updateTooltipPosition(event.clientX, event.clientY);
    }
}

function handleMouseLeave(index: number, point: DataPoint, event: MouseEvent) {
    if (props.hoverable) {
        ctx.hideTooltip();
    }
    emit('pointLeave', index, point, event);
}

// Check if scatter should be rendered
const shouldRender = computed(() =>
    props.series.visible !== false && points.value.length > 0
);
</script>

<template>
    <g v-if="shouldRender" class="ce-scatter">
        <path
            v-for="point in points"
            :key="point.index"
            class="ce-scatter-point"
            :class="{
                'ce-scatter-point--selected': isSelected(point.index),
                'ce-scatter-point--selectable': selectable,
                'ce-scatter-point--hoverable': hoverable
            }"
            :d="symbolPath"
            :transform="`translate(${point.x}, ${point.y})`"
            :fill="effectiveColor"
            :opacity="effectiveOpacity"
            :stroke="isSelected(point.index) ? '#000' : 'none'"
            :stroke-width="isSelected(point.index) ? 3 : 0"
            @click="handleClick(point.index, point.data)"
            @mouseenter="handleMouseEnter(point.index, point.data, $event)"
            @mousemove="handleMouseMove"
            @mouseleave="handleMouseLeave(point.index, point.data, $event)"
        />
    </g>
</template>

<style scoped>
.ce-scatter-point {
    transition: opacity 0.15s, stroke-width 0.15s;
}

.ce-scatter-point--hoverable {
    cursor: pointer;
}

.ce-scatter-point--hoverable:hover {
    opacity: 1 !important;
}

.ce-scatter-point--selectable {
    cursor: pointer;
}

.ce-scatter-point--selected {
    opacity: 1 !important;
}
</style>
