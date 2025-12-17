<script setup lang="ts">
/**
 * HBar - Horizontal bar glyph component
 *
 * Renders horizontal bars with support for:
 * - Variable left/right positions (for bandwidth-style charts)
 * - Custom colors per bar
 * - Opacity
 * - Hover and click events
 */

import { computed } from 'vue';
import { usePlotContext } from '../core/PlotContext';

export interface HBarDataPoint {
    /** Y position (category index or value) */
    y: number;
    /** Left edge value */
    left: number;
    /** Right edge value */
    right: number;
    /** Optional bar color */
    color?: string;
    /** Optional label for tooltip */
    label?: string;
    /** Any additional data */
    [key: string]: any;
}

const props = withDefaults(defineProps<{
    /** Array of bar data */
    data: HBarDataPoint[];
    /** Bar height as fraction of available space (0-1) */
    barHeight?: number;
    /** Default bar color */
    color?: string;
    /** Bar opacity */
    opacity?: number;
    /** Enable hover effects */
    hoverable?: boolean;
    /** Enable click events */
    clickable?: boolean;
    /** Unique name for this bar group */
    name?: string;
}>(), {
    barHeight: 0.8,
    color: '#2c90d9',
    opacity: 1,
    hoverable: true,
    clickable: false,
    name: 'hbar'
});

const emit = defineEmits<{
    /** Emitted when a bar is clicked */
    (e: 'barClick', index: number, data: HBarDataPoint): void;
    /** Emitted when mouse enters a bar */
    (e: 'barEnter', index: number, data: HBarDataPoint, event: MouseEvent): void;
    /** Emitted when mouse leaves a bar */
    (e: 'barLeave', index: number, data: HBarDataPoint, event: MouseEvent): void;
}>();

const ctx = usePlotContext();

// Calculate bar pixel height based on data range
const pixelBarHeight = computed(() => {
    if (props.data.length <= 1) {
        return 20 * props.barHeight; // Default height for single bar
    }

    // Calculate based on Y range
    const yValues = props.data.map(d => d.y);
    const yMin = Math.min(...yValues);
    const yMax = Math.max(...yValues);
    const yRange = yMax - yMin || 1;

    // Available height per bar
    const heightPerBar = ctx.dimensions.value.innerHeight / (yRange + 1);
    return heightPerBar * props.barHeight;
});

// Transform data to screen coordinates
const bars = computed(() => {
    return props.data.map((d, index) => {
        const xLeft = ctx.xScale.value(d.left);
        const xRight = ctx.xScale.value(d.right);
        const yCenter = ctx.yScale.value(d.y);

        // Ensure left < right for rendering
        const x = Math.min(xLeft, xRight);
        const width = Math.abs(xRight - xLeft);

        return {
            index,
            x,
            y: yCenter - pixelBarHeight.value / 2,
            width: Math.max(0, width), // Prevent negative width
            height: pixelBarHeight.value,
            color: d.color ?? props.color,
            data: d
        };
    });
});

// Event handlers
function handleClick(index: number, data: HBarDataPoint) {
    if (props.clickable) {
        emit('barClick', index, data);
    }
}

function handleMouseEnter(index: number, data: HBarDataPoint, event: MouseEvent) {
    if (props.hoverable) {
        ctx.showTooltip({
            point: { x: data.left, y: data.y, ...data },
            series: {
                id: props.name,
                name: data.label ?? props.name,
                data: [],
                color: data.color ?? props.color
            },
            screenX: event.clientX,
            screenY: event.clientY
        });
    }
    emit('barEnter', index, data, event);
}

function handleMouseMove(event: MouseEvent) {
    if (props.hoverable) {
        ctx.updateTooltipPosition(event.clientX, event.clientY);
    }
}

function handleMouseLeave(index: number, data: HBarDataPoint, event: MouseEvent) {
    if (props.hoverable) {
        ctx.hideTooltip();
    }
    emit('barLeave', index, data, event);
}
</script>

<template>
    <g class="ce-hbar" :data-name="name">
        <rect
            v-for="bar in bars"
            :key="bar.index"
            class="ce-hbar-bar"
            :class="{
                'ce-hbar-bar--hoverable': hoverable,
                'ce-hbar-bar--clickable': clickable
            }"
            :x="bar.x"
            :y="bar.y"
            :width="bar.width"
            :height="bar.height"
            :fill="bar.color"
            :opacity="opacity"
            @click="handleClick(bar.index, bar.data)"
            @mouseenter="handleMouseEnter(bar.index, bar.data, $event)"
            @mousemove="handleMouseMove"
            @mouseleave="handleMouseLeave(bar.index, bar.data, $event)"
        />
    </g>
</template>

<style scoped>
.ce-hbar-bar {
    transition: opacity 0.15s;
}

.ce-hbar-bar--hoverable:hover {
    opacity: 0.8 !important;
}

.ce-hbar-bar--clickable {
    cursor: pointer;
}
</style>
