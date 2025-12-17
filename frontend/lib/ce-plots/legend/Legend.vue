<script setup lang="ts">
/**
 * Legend - Legend container component
 *
 * Displays a legend for plot series with:
 * - Configurable position (top, bottom, left, right, or floating)
 * - Visibility toggles for each series
 * - Collapsible groups
 * - Custom styling options
 */

import { computed, ref } from 'vue';
import type { DataSeries } from '../types';
import LegendItem from './LegendItem.vue';

export interface LegendGroup {
    id: string;
    name: string;
    series: DataSeries[];
    collapsed?: boolean;
}

const props = withDefaults(defineProps<{
    /** Series to display */
    series: DataSeries[];
    /** Optional grouping of series */
    groups?: LegendGroup[];
    /** Legend position */
    position?: 'top' | 'bottom' | 'left' | 'right' | 'float';
    /** For floating position: x offset */
    floatX?: number;
    /** For floating position: y offset */
    floatY?: number;
    /** Layout direction */
    orientation?: 'horizontal' | 'vertical';
    /** Show visibility checkboxes */
    showCheckboxes?: boolean;
    /** Allow collapsing groups */
    collapsible?: boolean;
    /** Maximum height before scrolling (for vertical) */
    maxHeight?: string;
    /** Custom CSS class */
    legendClass?: string;
    /** Function to get series color */
    getSeriesColor?: (series: DataSeries, index: number) => string;
    /** Function to get series symbol */
    getSeriesSymbol?: (series: DataSeries, index: number) => string;
    /** Function to get series dash pattern */
    getSeriesDash?: (series: DataSeries, index: number) => string;
}>(), {
    position: 'right',
    orientation: 'vertical',
    showCheckboxes: true,
    collapsible: true,
    floatX: 10,
    floatY: 10
});

const emit = defineEmits<{
    (e: 'toggle', seriesId: string): void;
    (e: 'select', seriesId: string): void;
    (e: 'toggleGroup', groupId: string): void;
}>();

// Track collapsed state for groups
const collapsedGroups = ref<Set<string>>(new Set());

// Default color getter
function defaultGetColor(series: DataSeries, index: number): string {
    return series.color ?? `hsl(${(index * 137.5) % 360}, 70%, 50%)`;
}

// Default symbol getter
function defaultGetSymbol(series: DataSeries): string {
    return series.symbol ?? 'circle';
}

// Default dash getter
function defaultGetDash(series: DataSeries): string {
    return series.dash ?? 'solid';
}

// Compute effective getters
const getColor = computed(() => props.getSeriesColor ?? defaultGetColor);
const getSymbol = computed(() => props.getSeriesSymbol ?? defaultGetSymbol);
const getDash = computed(() => props.getSeriesDash ?? defaultGetDash);

// Compute position styles
const positionStyle = computed(() => {
    if (props.position === 'float') {
        return {
            position: 'absolute' as const,
            left: `${props.floatX}px`,
            top: `${props.floatY}px`
        };
    }
    return {};
});

// Toggle group collapsed state
function toggleGroup(groupId: string) {
    if (collapsedGroups.value.has(groupId)) {
        collapsedGroups.value.delete(groupId);
    } else {
        collapsedGroups.value.add(groupId);
    }
    collapsedGroups.value = new Set(collapsedGroups.value);
    emit('toggleGroup', groupId);
}

function isGroupCollapsed(groupId: string): boolean {
    return collapsedGroups.value.has(groupId);
}

function handleToggle(seriesId: string) {
    emit('toggle', seriesId);
}

function handleSelect(seriesId: string) {
    emit('select', seriesId);
}
</script>

<template>
    <div
        class="ce-legend"
        :class="[
            legendClass,
            `ce-legend--${position}`,
            `ce-legend--${orientation}`
        ]"
        :style="[positionStyle, maxHeight ? { maxHeight, overflowY: 'auto' } : {}]"
    >
        <slot name="header"></slot>

        <!-- Grouped display -->
        <template v-if="groups && groups.length > 0">
            <div
                v-for="group in groups"
                :key="group.id"
                class="ce-legend-group"
            >
                <!-- Group header -->
                <div
                    v-if="group.name"
                    class="ce-legend-group-header"
                    :class="{ 'ce-legend-group-header--collapsible': collapsible }"
                    @click="collapsible && toggleGroup(group.id)"
                >
                    <span
                        v-if="collapsible"
                        class="ce-legend-collapse-icon"
                        :class="{ 'ce-legend-collapse-icon--collapsed': isGroupCollapsed(group.id) }"
                    >
                        ▼
                    </span>
                    <span class="ce-legend-group-name">{{ group.name }}</span>
                </div>

                <!-- Group items -->
                <div
                    v-show="!isGroupCollapsed(group.id)"
                    class="ce-legend-group-items"
                >
                    <LegendItem
                        v-for="(s, index) in group.series"
                        :key="s.id"
                        :series="s"
                        :color="getColor(s, index)"
                        :symbol="getSymbol(s, index)"
                        :dash="getDash(s, index)"
                        :show-checkbox="showCheckboxes"
                        @toggle="handleToggle"
                        @click="handleSelect"
                    />
                </div>
            </div>
        </template>

        <!-- Flat display (no groups) -->
        <template v-else>
            <LegendItem
                v-for="(s, index) in series"
                :key="s.id"
                :series="s"
                :color="getColor(s, index)"
                :symbol="getSymbol(s, index)"
                :dash="getDash(s, index)"
                :show-checkbox="showCheckboxes"
                @toggle="handleToggle"
                @click="handleSelect"
            />
        </template>

        <slot name="footer"></slot>
    </div>
</template>

<style scoped>
.ce-legend {
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 8px;
    font-size: 12px;
    font-family: system-ui, -apple-system, sans-serif;
}

/* Position variants */
.ce-legend--float {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    z-index: 10;
}

.ce-legend--top,
.ce-legend--bottom {
    width: 100%;
}

.ce-legend--left,
.ce-legend--right {
    min-width: 120px;
    max-width: 200px;
}

/* Orientation variants */
.ce-legend--horizontal {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
}

.ce-legend--horizontal .ce-legend-group {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 4px;
}

.ce-legend--horizontal .ce-legend-group-items {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
}

.ce-legend--vertical {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

/* Group styles */
.ce-legend-group {
    margin-bottom: 8px;
}

.ce-legend-group:last-child {
    margin-bottom: 0;
}

.ce-legend-group-header {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 4px 0;
    font-weight: 600;
    color: #555;
    border-bottom: 1px solid #eee;
    margin-bottom: 4px;
}

.ce-legend-group-header--collapsible {
    cursor: pointer;
}

.ce-legend-group-header--collapsible:hover {
    color: #333;
}

.ce-legend-collapse-icon {
    font-size: 10px;
    transition: transform 0.2s ease;
}

.ce-legend-collapse-icon--collapsed {
    transform: rotate(-90deg);
}

.ce-legend-group-name {
    flex: 1;
}

.ce-legend-group-items {
    padding-left: 4px;
}
</style>
