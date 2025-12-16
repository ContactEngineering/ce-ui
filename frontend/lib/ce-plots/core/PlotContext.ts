/**
 * PlotContext - Provide/Inject context for plot components
 *
 * This module defines the context that is provided by the Plot component
 * and injected by child components (axes, glyphs, etc.) to access shared
 * plot state like scales, dimensions, and transforms.
 */

import type { InjectionKey, Ref, ComputedRef } from 'vue';
import type {
    PlotDimensions,
    ZoomTransform,
    NumericScale,
    SelectionState,
    TooltipContext,
    PlotTheme
} from '../types';

/**
 * The plot context interface that child components can inject
 */
export interface PlotContext {
    /** Current plot dimensions (reactive) */
    dimensions: Ref<PlotDimensions>;

    /** X-axis scale (reactive, includes zoom transform) */
    xScale: ComputedRef<NumericScale>;

    /** Y-axis scale (reactive, includes zoom transform) */
    yScale: ComputedRef<NumericScale>;

    /** Original X scale without zoom (for axis rendering) */
    xScaleOriginal: ComputedRef<NumericScale>;

    /** Original Y scale without zoom (for axis rendering) */
    yScaleOriginal: ComputedRef<NumericScale>;

    /** Current zoom/pan transform */
    transform: Ref<ZoomTransform>;

    /** Current selection state */
    selection: Ref<SelectionState>;

    /** Current theme */
    theme: PlotTheme;

    /** Get color for a series based on index and child status */
    getSeriesColor: (index: number, total: number, isChild: boolean) => string;

    /** Show tooltip */
    showTooltip: (context: TooltipContext) => void;

    /** Hide tooltip */
    hideTooltip: () => void;

    /** Update tooltip position */
    updateTooltipPosition: (screenX: number, screenY: number) => void;

    /** Select a point */
    selectPoint: (seriesId: string, pointIndex: number) => void;

    /** Clear selection */
    clearSelection: () => void;
}

/**
 * Injection key for the plot context
 * Use this with inject() in child components
 */
export const PlotContextKey: InjectionKey<PlotContext> = Symbol('PlotContext');

/**
 * Helper function to inject plot context with error handling
 */
export function usePlotContext(): PlotContext {
    const context = inject(PlotContextKey);
    if (!context) {
        throw new Error(
            'usePlotContext() must be called inside a <Plot> component. ' +
            'Make sure your component is a child of <Plot>.'
        );
    }
    return context;
}

// Need to import inject for the helper function
import { inject } from 'vue';
