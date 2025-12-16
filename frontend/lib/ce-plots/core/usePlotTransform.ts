/**
 * usePlotTransform - Composable for zoom and pan behavior
 *
 * Handles:
 * - D3 zoom behavior setup
 * - Zoom/pan state management
 * - Reset to initial view
 * - Zoom constraints
 */

import { ref, onMounted, onUnmounted, watch, type Ref } from 'vue';
import { zoom, zoomIdentity, type ZoomBehavior, type D3ZoomEvent } from 'd3-zoom';
import { select } from 'd3-selection';
import type { ZoomTransform, PlotDimensions } from '../types';

export interface UsePlotTransformOptions {
    /** Whether zoom/pan is enabled (default: true) */
    enabled?: boolean;
    /** Minimum and maximum scale factors [min, max] */
    scaleExtent?: [number, number];
    /** Callback when transform changes */
    onTransform?: (transform: ZoomTransform) => void;
    /** Whether to constrain pan to data bounds */
    constrainPan?: boolean;
    /** Reactive dimensions (for extent calculations) */
    dimensions?: Ref<PlotDimensions>;
}

export interface UsePlotTransformReturn {
    /** Current zoom transform (reactive) */
    transform: Ref<ZoomTransform>;
    /** Reset zoom to identity (1:1, no pan) */
    resetZoom: () => void;
    /** Zoom to a specific scale factor */
    zoomTo: (scale: number, animate?: boolean) => void;
    /** Pan by a delta */
    panBy: (dx: number, dy: number, animate?: boolean) => void;
    /** Whether zoom is currently at identity */
    isAtIdentity: Ref<boolean>;
    /** Initialize zoom behavior on an SVG element */
    initZoom: (svgElement: SVGSVGElement) => void;
    /** Cleanup zoom behavior */
    cleanup: () => void;
}

export function usePlotTransform(options: UsePlotTransformOptions = {}): UsePlotTransformReturn {
    const {
        enabled = true,
        scaleExtent = [0.5, 20],
        onTransform,
        constrainPan = false,
        dimensions
    } = options;

    // Current transform state
    const transform = ref<ZoomTransform>({
        x: 0,
        y: 0,
        k: 1
    });

    // Track if at identity
    const isAtIdentity = ref(true);

    // D3 zoom behavior instance
    let zoomBehavior: ZoomBehavior<SVGSVGElement, unknown> | null = null;
    let svgElement: SVGSVGElement | null = null;

    /**
     * Handle zoom events from D3
     */
    function handleZoom(event: D3ZoomEvent<SVGSVGElement, unknown>) {
        const t = event.transform;

        transform.value = {
            x: t.x,
            y: t.y,
            k: t.k
        };

        isAtIdentity.value = t.k === 1 && t.x === 0 && t.y === 0;

        onTransform?.(transform.value);
    }

    /**
     * Initialize zoom behavior on SVG element
     */
    function initZoom(element: SVGSVGElement) {
        if (!enabled) return;

        svgElement = element;

        zoomBehavior = zoom<SVGSVGElement, unknown>()
            .scaleExtent(scaleExtent)
            .on('zoom', handleZoom);

        // Apply translate extent if constraining pan
        if (constrainPan && dimensions) {
            zoomBehavior.translateExtent([
                [0, 0],
                [dimensions.value.innerWidth, dimensions.value.innerHeight]
            ]);
        }

        // Filter to only allow zoom on plot area, not on UI elements
        zoomBehavior.filter((event: any) => {
            // Allow wheel events for zoom
            if (event.type === 'wheel') return true;
            // Allow drag events (mousedown + mousemove)
            if (event.type === 'mousedown') return true;
            // Allow touch events
            if (event.type === 'touchstart') return true;
            return false;
        });

        select(element).call(zoomBehavior);
    }

    /**
     * Reset zoom to identity transform
     */
    function resetZoom() {
        if (!svgElement || !zoomBehavior) return;

        select(svgElement)
            .transition()
            .duration(300)
            .call(zoomBehavior.transform, zoomIdentity);
    }

    /**
     * Zoom to a specific scale factor
     */
    function zoomTo(scale: number, animate: boolean = true) {
        if (!svgElement || !zoomBehavior) return;

        const selection = select(svgElement);
        const targetTransform = zoomIdentity.scale(scale);

        if (animate) {
            selection
                .transition()
                .duration(300)
                .call(zoomBehavior.transform, targetTransform);
        } else {
            selection.call(zoomBehavior.transform, targetTransform);
        }
    }

    /**
     * Pan by a delta
     */
    function panBy(dx: number, dy: number, animate: boolean = true) {
        if (!svgElement || !zoomBehavior) return;

        const selection = select(svgElement);
        const currentTransform = zoomIdentity
            .translate(transform.value.x + dx, transform.value.y + dy)
            .scale(transform.value.k);

        if (animate) {
            selection
                .transition()
                .duration(150)
                .call(zoomBehavior.transform, currentTransform);
        } else {
            selection.call(zoomBehavior.transform, currentTransform);
        }
    }

    /**
     * Cleanup zoom behavior
     */
    function cleanup() {
        if (svgElement) {
            select(svgElement).on('.zoom', null);
        }
        zoomBehavior = null;
        svgElement = null;
    }

    // Update translate extent when dimensions change
    if (constrainPan && dimensions) {
        watch(dimensions, () => {
            if (zoomBehavior && dimensions.value) {
                zoomBehavior.translateExtent([
                    [0, 0],
                    [dimensions.value.innerWidth, dimensions.value.innerHeight]
                ]);
            }
        });
    }

    // Cleanup on unmount
    onUnmounted(cleanup);

    return {
        transform,
        resetZoom,
        zoomTo,
        panBy,
        isAtIdentity,
        initZoom,
        cleanup
    };
}
