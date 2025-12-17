/**
 * useTooltip - Composable for tooltip state management
 *
 * Provides reactive tooltip state that can be used independently
 * or integrated with the Plot component's context.
 */

import { ref, computed, type Ref } from 'vue';
import type { DataPoint, DataSeries, TooltipContext } from '../types';

export interface UseTooltipOptions {
    /** Offset from cursor position */
    offset?: { x: number; y: number };
    /** Delay before showing tooltip (ms) */
    showDelay?: number;
    /** Delay before hiding tooltip (ms) */
    hideDelay?: number;
}

export interface UseTooltipReturn {
    /** Whether tooltip is visible */
    visible: Ref<boolean>;
    /** Current tooltip context (point, series, position) */
    context: Ref<TooltipContext | null>;
    /** Screen position for tooltip */
    position: Ref<{ x: number; y: number }>;
    /** Show tooltip for a point */
    show: (context: TooltipContext) => void;
    /** Hide tooltip */
    hide: () => void;
    /** Update tooltip position (for mouse move) */
    updatePosition: (screenX: number, screenY: number) => void;
    /** Computed style object for positioning */
    style: Ref<Record<string, string>>;
}

export function useTooltip(options: UseTooltipOptions = {}): UseTooltipReturn {
    const {
        offset = { x: 12, y: 12 },
        showDelay = 0,
        hideDelay = 100
    } = options;

    const visible = ref(false);
    const context = ref<TooltipContext | null>(null);
    const position = ref({ x: 0, y: 0 });

    let showTimeout: ReturnType<typeof setTimeout> | null = null;
    let hideTimeout: ReturnType<typeof setTimeout> | null = null;

    /**
     * Clear any pending timeouts
     */
    function clearTimeouts() {
        if (showTimeout) {
            clearTimeout(showTimeout);
            showTimeout = null;
        }
        if (hideTimeout) {
            clearTimeout(hideTimeout);
            hideTimeout = null;
        }
    }

    /**
     * Show tooltip for a data point
     */
    function show(ctx: TooltipContext) {
        clearTimeouts();

        const doShow = () => {
            context.value = ctx;
            position.value = { x: ctx.screenX, y: ctx.screenY };
            visible.value = true;
        };

        if (showDelay > 0) {
            showTimeout = setTimeout(doShow, showDelay);
        } else {
            doShow();
        }
    }

    /**
     * Hide tooltip
     */
    function hide() {
        clearTimeouts();

        const doHide = () => {
            visible.value = false;
            // Keep context for fade-out animation
        };

        if (hideDelay > 0) {
            hideTimeout = setTimeout(doHide, hideDelay);
        } else {
            doHide();
        }
    }

    /**
     * Update tooltip position (call on mousemove)
     */
    function updatePosition(screenX: number, screenY: number) {
        position.value = { x: screenX, y: screenY };
        if (context.value) {
            context.value = {
                ...context.value,
                screenX,
                screenY
            };
        }
    }

    /**
     * Computed style for tooltip positioning
     */
    const style = computed(() => {
        return {
            position: 'fixed',
            left: `${position.value.x + offset.x}px`,
            top: `${position.value.y + offset.y}px`,
            pointerEvents: 'none',
            zIndex: '1000',
            opacity: visible.value ? '1' : '0',
            transition: 'opacity 0.15s ease-in-out'
        };
    });

    return {
        visible,
        context,
        position,
        show,
        hide,
        updatePosition,
        style
    };
}
