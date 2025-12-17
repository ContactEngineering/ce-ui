<script setup lang="ts">
/**
 * LegendItem - Individual legend entry component
 *
 * Displays a single series in the legend with:
 * - Color/symbol indicator
 * - Series name
 * - Visibility toggle
 * - Click to toggle visibility
 */

import { computed } from 'vue';
import type { DataSeries } from '../types';

const props = withDefaults(defineProps<{
    /** Series data */
    series: DataSeries;
    /** Color for this series */
    color: string;
    /** Symbol type (circle, cross, diamond, etc.) */
    symbol?: string;
    /** Line dash pattern */
    dash?: string;
    /** Whether to show visibility checkbox */
    showCheckbox?: boolean;
    /** Custom CSS class */
    itemClass?: string;
}>(), {
    symbol: 'circle',
    showCheckbox: true
});

const emit = defineEmits<{
    (e: 'toggle', seriesId: string): void;
    (e: 'click', seriesId: string): void;
}>();

// Compute symbol path for SVG
const symbolPath = computed(() => {
    const size = 8;
    const half = size / 2;

    switch (props.symbol) {
        case 'cross':
        case 'x':
            return `M${-half},${-half}L${half},${half}M${-half},${half}L${half},${-half}`;
        case 'diamond':
            return `M0,${-half}L${half},0L0,${half}L${-half},0Z`;
        case 'square':
            return `M${-half},${-half}H${half}V${half}H${-half}Z`;
        case 'triangle':
            return `M0,${-half}L${half},${half}H${-half}Z`;
        case 'circle':
        default:
            return null; // Use circle element instead
    }
});

// Compute line dash array
const dashArray = computed(() => {
    if (!props.dash) return undefined;

    switch (props.dash) {
        case 'dashed':
            return '4,4';
        case 'dotted':
            return '2,2';
        case 'dashdot':
            return '4,2,2,2';
        default:
            return props.dash;
    }
});

function handleClick() {
    emit('click', props.series.id);
}

function handleToggle(event: Event) {
    event.stopPropagation();
    emit('toggle', props.series.id);
}
</script>

<template>
    <div
        class="ce-legend-item"
        :class="[
            itemClass,
            { 'ce-legend-item--hidden': !series.visible }
        ]"
        @click="handleClick"
    >
        <!-- Checkbox for visibility toggle -->
        <input
            v-if="showCheckbox"
            type="checkbox"
            :checked="series.visible !== false"
            class="ce-legend-checkbox"
            @change="handleToggle"
        />

        <!-- Symbol indicator -->
        <svg class="ce-legend-symbol" width="24" height="16" viewBox="-12 -8 24 16">
            <!-- Line -->
            <line
                x1="-10"
                y1="0"
                x2="10"
                y2="0"
                :stroke="color"
                stroke-width="2"
                :stroke-dasharray="dashArray"
                :opacity="series.visible !== false ? 1 : 0.4"
            />

            <!-- Symbol marker -->
            <g transform="translate(0, 0)">
                <circle
                    v-if="!symbolPath"
                    r="4"
                    :fill="color"
                    :opacity="series.visible !== false ? 1 : 0.4"
                />
                <path
                    v-else
                    :d="symbolPath"
                    :stroke="color"
                    :fill="symbol === 'diamond' || symbol === 'square' || symbol === 'triangle' ? color : 'none'"
                    stroke-width="2"
                    :opacity="series.visible !== false ? 1 : 0.4"
                />
            </g>
        </svg>

        <!-- Series name -->
        <span
            class="ce-legend-label"
            :style="{ opacity: series.visible !== false ? 1 : 0.5 }"
        >
            {{ series.name }}
        </span>
    </div>
</template>

<style scoped>
.ce-legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 4px 8px;
    cursor: pointer;
    border-radius: 4px;
    transition: background-color 0.15s ease;
    user-select: none;
}

.ce-legend-item:hover {
    background-color: rgba(0, 0, 0, 0.05);
}

.ce-legend-item--hidden {
    opacity: 0.6;
}

.ce-legend-checkbox {
    margin: 0;
    cursor: pointer;
}

.ce-legend-symbol {
    flex-shrink: 0;
}

.ce-legend-label {
    font-size: 12px;
    font-family: system-ui, -apple-system, sans-serif;
    color: #333;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
</style>
