<script setup lang="ts">
/**
 * Tooltip - Tooltip overlay component
 *
 * Displays information about hovered data points with:
 * - Default formatting for point data
 * - Custom content via slot
 * - Automatic positioning near cursor
 * - Support for HTML content (images, rich text)
 */

import { computed } from 'vue';
import type { TooltipContext } from '../types';
import { formatExponential } from '../axes/formatters';

const props = withDefaults(defineProps<{
    /** Whether tooltip is visible */
    visible: boolean;
    /** Tooltip context with point, series, position */
    context: TooltipContext | null;
    /** Screen position */
    position: { x: number; y: number };
    /** Offset from cursor */
    offset?: { x: number; y: number };
    /** Custom CSS class */
    tooltipClass?: string;
    /** Show series color indicator */
    showColorIndicator?: boolean;
    /** Format function for values */
    formatValue?: (value: number) => string;
}>(), {
    offset: () => ({ x: 12, y: 12 }),
    showColorIndicator: true,
    formatValue: formatExponential
});

// Compute position style
const positionStyle = computed(() => ({
    position: 'fixed' as const,
    left: `${props.position.x + props.offset.x}px`,
    top: `${props.position.y + props.offset.y}px`,
    pointerEvents: 'none' as const,
    zIndex: 1000
}));

// Format point data for display
const formattedData = computed(() => {
    if (!props.context) return null;

    const { point, series } = props.context;

    return {
        seriesName: series.name,
        seriesColor: series.color ?? '#333',
        x: props.formatValue(point.x),
        y: props.formatValue(point.y),
        // Include any additional point data
        extra: Object.entries(point)
            .filter(([key]) => !['x', 'y'].includes(key))
            .filter(([_, value]) => value !== undefined && value !== null)
            .map(([key, value]) => ({
                key,
                value: typeof value === 'number' ? props.formatValue(value) : String(value)
            }))
    };
});
</script>

<template>
    <Teleport to="body">
        <Transition name="tooltip">
            <div
                v-if="visible && context"
                class="ce-tooltip"
                :class="tooltipClass"
                :style="positionStyle"
            >
                <slot :context="context" :formatted="formattedData">
                    <!-- Default tooltip content -->
                    <div class="ce-tooltip-content">
                        <!-- Series name with color indicator -->
                        <div class="ce-tooltip-header">
                            <span
                                v-if="showColorIndicator"
                                class="ce-tooltip-color"
                                :style="{ backgroundColor: formattedData?.seriesColor }"
                            ></span>
                            <strong>{{ formattedData?.seriesName }}</strong>
                        </div>

                        <!-- X/Y values -->
                        <div class="ce-tooltip-row">
                            <span class="ce-tooltip-label">x:</span>
                            <span class="ce-tooltip-value">{{ formattedData?.x }}</span>
                        </div>
                        <div class="ce-tooltip-row">
                            <span class="ce-tooltip-label">y:</span>
                            <span class="ce-tooltip-value">{{ formattedData?.y }}</span>
                        </div>

                        <!-- Extra data fields -->
                        <div
                            v-for="extra in formattedData?.extra"
                            :key="extra.key"
                            class="ce-tooltip-row"
                        >
                            <span class="ce-tooltip-label">{{ extra.key }}:</span>
                            <span class="ce-tooltip-value">{{ extra.value }}</span>
                        </div>
                    </div>
                </slot>
            </div>
        </Transition>
    </Teleport>
</template>

<style scoped>
.ce-tooltip {
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    font-size: 12px;
    font-family: system-ui, -apple-system, sans-serif;
    max-width: 300px;
}

.ce-tooltip-content {
    padding: 8px 12px;
}

.ce-tooltip-header {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 6px;
    padding-bottom: 6px;
    border-bottom: 1px solid #eee;
}

.ce-tooltip-color {
    width: 10px;
    height: 10px;
    border-radius: 2px;
    flex-shrink: 0;
}

.ce-tooltip-row {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    line-height: 1.4;
}

.ce-tooltip-label {
    color: #666;
}

.ce-tooltip-value {
    font-family: ui-monospace, monospace;
    color: #333;
}

/* Transition */
.tooltip-enter-active,
.tooltip-leave-active {
    transition: opacity 0.15s ease;
}

.tooltip-enter-from,
.tooltip-leave-to {
    opacity: 0;
}
</style>
