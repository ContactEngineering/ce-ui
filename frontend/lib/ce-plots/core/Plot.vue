<script setup lang="ts">
/**
 * Plot - Main container component for ce-plots
 *
 * This component provides:
 * - SVG container with proper dimensions
 * - Plot context for child components (axes, glyphs)
 * - Zoom/pan behavior
 * - Selection state
 * - Tooltip coordination
 * - Color palette management
 */

import { ref, computed, provide, onMounted, watch, toRef } from 'vue';
import { usePlotDimensions } from './usePlotDimensions';
import { usePlotScales } from './usePlotScales';
import { usePlotTransform } from './usePlotTransform';
import { PlotContextKey, type PlotContext } from './PlotContext';
import type {
    PlotConfig,
    DataSeries,
    SelectionState,
    TooltipContext,
    ZoomTransform,
    PlotTheme,
    DataPoint
} from '../types';
import { DEFAULT_THEME } from '../types';

// ============================================================================
// Props & Emits
// ============================================================================

const props = withDefaults(defineProps<{
    /** Plot configuration (axes, margins, etc.) */
    config: PlotConfig;
    /** Data series to display */
    series?: DataSeries[];
    /** Custom theme overrides */
    theme?: Partial<PlotTheme>;
    /** Enable zoom/pan (default: true) */
    zoomEnabled?: boolean;
    /** Enable point selection (default: false) */
    selectionEnabled?: boolean;
}>(), {
    series: () => [],
    zoomEnabled: true,
    selectionEnabled: false
});

const emit = defineEmits<{
    /** Emitted when a point is selected */
    (e: 'select', seriesId: string, pointIndex: number, point: DataPoint): void;
    /** Emitted when selection is cleared */
    (e: 'deselect'): void;
    /** Emitted when zoom/pan changes */
    (e: 'zoom', transform: ZoomTransform): void;
    /** Emitted when zoom is reset */
    (e: 'zoomReset'): void;
}>();

// ============================================================================
// Template Refs
// ============================================================================

const containerRef = ref<HTMLElement | null>(null);
const svgRef = ref<SVGSVGElement | null>(null);

// ============================================================================
// Reactive Series
// ============================================================================

const seriesRef = toRef(props, 'series');

// ============================================================================
// Theme
// ============================================================================

const theme: PlotTheme = {
    ...DEFAULT_THEME,
    ...props.theme
};

// ============================================================================
// Dimensions
// ============================================================================

const { dimensions, setFixedDimensions, resetToResponsive } = usePlotDimensions(
    containerRef,
    { config: props.config }
);

// ============================================================================
// Transform (Zoom/Pan)
// ============================================================================

const { transform, resetZoom, zoomTo, isAtIdentity, initZoom } = usePlotTransform({
    enabled: props.zoomEnabled,
    onTransform: (t) => emit('zoom', t),
    dimensions
});

// ============================================================================
// Scales
// ============================================================================

const { xScale, yScale, xScaleOriginal, yScaleOriginal } = usePlotScales({
    config: props.config,
    dimensions,
    series: seriesRef,
    transform
});

// ============================================================================
// Selection State
// ============================================================================

const selection = ref<SelectionState>({
    seriesId: null,
    pointIndex: null
});

function selectPoint(seriesId: string, pointIndex: number) {
    // Toggle if already selected
    if (selection.value.seriesId === seriesId && selection.value.pointIndex === pointIndex) {
        clearSelection();
        return;
    }

    selection.value = { seriesId, pointIndex };

    // Find the actual point data
    const series = props.series.find(s => s.id === seriesId);
    if (series && series.data[pointIndex]) {
        emit('select', seriesId, pointIndex, series.data[pointIndex]);
    }
}

function clearSelection() {
    selection.value = { seriesId: null, pointIndex: null };
    emit('deselect');
}

// ============================================================================
// Tooltip State
// ============================================================================

const tooltipVisible = ref(false);
const tooltipContext = ref<TooltipContext | null>(null);

function showTooltip(context: TooltipContext) {
    tooltipContext.value = context;
    tooltipVisible.value = true;
}

function hideTooltip() {
    tooltipVisible.value = false;
}

function updateTooltipPosition(screenX: number, screenY: number) {
    if (tooltipContext.value) {
        tooltipContext.value = {
            ...tooltipContext.value,
            screenX,
            screenY
        };
    }
}

// ============================================================================
// Color Palette
// ============================================================================

// Import palettes (we'll create these files later, use simple fallbacks for now)
const PLASMA_FALLBACK = ['#0d0887', '#46039f', '#7201a8', '#9c179e', '#bd3786', '#d8576b', '#ed7953', '#fb9f3a', '#fdca26', '#f0f921'];
const GREYS_FALLBACK = ['#000000', '#1a1a1a', '#333333', '#4d4d4d', '#666666', '#808080', '#999999', '#b3b3b3', '#cccccc', '#e6e6e6'];

function getSeriesColor(index: number, total: number, isChild: boolean): string {
    const palette = isChild ? PLASMA_FALLBACK : GREYS_FALLBACK;
    const paletteIndex = Math.floor((index / Math.max(total, 1)) * (palette.length - 1));
    return palette[Math.min(paletteIndex, palette.length - 1)];
}

// ============================================================================
// Provide Context
// ============================================================================

const plotContext: PlotContext = {
    dimensions,
    xScale,
    yScale,
    xScaleOriginal,
    yScaleOriginal,
    transform,
    selection,
    theme,
    getSeriesColor,
    showTooltip,
    hideTooltip,
    updateTooltipPosition,
    selectPoint,
    clearSelection
};

provide(PlotContextKey, plotContext);

// ============================================================================
// Lifecycle
// ============================================================================

onMounted(() => {
    if (svgRef.value && props.zoomEnabled) {
        initZoom(svgRef.value);
    }
});

// Watch for zoomEnabled changes
watch(() => props.zoomEnabled, (enabled) => {
    if (enabled && svgRef.value) {
        initZoom(svgRef.value);
    }
});

// ============================================================================
// Exposed Methods
// ============================================================================

function handleResetZoom() {
    resetZoom();
    emit('zoomReset');
}

defineExpose({
    /** Reset zoom to 1:1 */
    resetZoom: handleResetZoom,
    /** Zoom to specific scale */
    zoomTo,
    /** Set fixed dimensions (for print) */
    setFixedDimensions,
    /** Reset to responsive sizing */
    resetToResponsive,
    /** Clear current selection */
    clearSelection,
    /** Get current dimensions */
    getDimensions: () => dimensions.value,
    /** Get SVG element for export */
    getSvgElement: () => svgRef.value
});
</script>

<template>
    <div ref="containerRef" class="ce-plot">
        <svg
            ref="svgRef"
            :width="dimensions.width"
            :height="dimensions.height"
            class="ce-plot-svg"
        >
            <!-- Clip path for plot area -->
            <defs>
                <clipPath id="plot-area-clip">
                    <rect
                        :width="dimensions.innerWidth"
                        :height="dimensions.innerHeight"
                    />
                </clipPath>
            </defs>

            <!-- Main plot group with margins -->
            <g
                class="ce-plot-main"
                :transform="`translate(${dimensions.margins.left},${dimensions.margins.top})`"
            >
                <!-- Background rect for zoom/pan events -->
                <rect
                    class="ce-plot-background"
                    :width="dimensions.innerWidth"
                    :height="dimensions.innerHeight"
                    fill="transparent"
                />

                <!-- Grid slot (rendered below data) -->
                <g class="ce-plot-grid">
                    <slot name="grid"></slot>
                </g>

                <!-- Clipped area for data rendering -->
                <g class="ce-plot-data" clip-path="url(#plot-area-clip)">
                    <slot></slot>
                </g>

                <!-- Axes slot (rendered on top of data) -->
                <g class="ce-plot-axes">
                    <slot name="axes"></slot>
                </g>
            </g>
        </svg>

        <!-- Overlay slot for tooltips, legends, etc. -->
        <div class="ce-plot-overlay">
            <slot
                name="overlay"
                :tooltip-visible="tooltipVisible"
                :tooltip-context="tooltipContext"
                :selection="selection"
            ></slot>
        </div>
    </div>
</template>

<style scoped>
.ce-plot {
    position: relative;
    width: 100%;
}

.ce-plot-svg {
    display: block;
    overflow: visible;
}

.ce-plot-background {
    cursor: grab;
}

.ce-plot-background:active {
    cursor: grabbing;
}

.ce-plot-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
}

.ce-plot-overlay > * {
    pointer-events: auto;
}
</style>
