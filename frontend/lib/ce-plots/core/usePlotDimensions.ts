/**
 * usePlotDimensions - Composable for responsive plot sizing
 *
 * Handles:
 * - ResizeObserver for responsive container tracking
 * - Aspect ratio calculations
 * - Margin management
 * - Minimum dimension constraints
 */

import { ref, onMounted, onUnmounted, watch, type Ref } from 'vue';
import type { PlotConfig, PlotDimensions, PlotMargins } from '../types';
import { DEFAULT_MARGINS } from '../types';

export interface UsePlotDimensionsOptions {
    /** Plot configuration */
    config: PlotConfig;
    /** Fixed width override (disables responsive width) */
    fixedWidth?: number;
    /** Fixed height override (disables responsive height) */
    fixedHeight?: number;
}

export interface UsePlotDimensionsReturn {
    /** Reactive dimensions object */
    dimensions: Ref<PlotDimensions>;
    /** Force a dimension recalculation */
    updateDimensions: () => void;
    /** Set fixed dimensions (useful for print layouts) */
    setFixedDimensions: (width: number, height: number) => void;
    /** Reset to responsive mode */
    resetToResponsive: () => void;
}

export function usePlotDimensions(
    container: Ref<HTMLElement | null>,
    options: UsePlotDimensionsOptions
): UsePlotDimensionsReturn {
    const { config } = options;

    // Merge margins with defaults
    const margins: PlotMargins = {
        ...DEFAULT_MARGINS,
        ...config.margins
    };

    // Track whether we're in fixed mode
    const isFixedMode = ref(false);
    const fixedWidth = ref<number | null>(options.fixedWidth ?? null);
    const fixedHeight = ref<number | null>(options.fixedHeight ?? null);

    // Initialize with sensible defaults
    const dimensions = ref<PlotDimensions>({
        width: 400,
        height: 300,
        innerWidth: 400 - margins.left - margins.right,
        innerHeight: 300 - margins.top - margins.bottom,
        margins
    });

    let resizeObserver: ResizeObserver | null = null;

    /**
     * Calculate dimensions based on container size and config
     */
    function updateDimensions() {
        let width: number;
        let height: number;

        if (isFixedMode.value && fixedWidth.value !== null && fixedHeight.value !== null) {
            // Fixed mode: use specified dimensions
            width = fixedWidth.value;
            height = fixedHeight.value;
        } else if (container.value) {
            // Responsive mode: measure container
            const rect = container.value.getBoundingClientRect();
            width = rect.width;

            if (config.aspectRatio) {
                // Calculate height from aspect ratio
                height = width / config.aspectRatio;
            } else if (rect.height > 0) {
                // Use container height
                height = rect.height;
            } else {
                // Fallback default
                height = 300;
            }
        } else {
            // No container yet, use defaults
            return;
        }

        // Apply minimum constraints
        if (config.minWidth) {
            width = Math.max(width, config.minWidth);
        }
        if (config.minHeight) {
            height = Math.max(height, config.minHeight);
        }

        // Calculate inner dimensions
        const innerWidth = Math.max(0, width - margins.left - margins.right);
        const innerHeight = Math.max(0, height - margins.top - margins.bottom);

        dimensions.value = {
            width,
            height,
            innerWidth,
            innerHeight,
            margins
        };
    }

    /**
     * Set fixed dimensions (useful for print layouts)
     */
    function setFixedDimensions(width: number, height: number) {
        isFixedMode.value = true;
        fixedWidth.value = width;
        fixedHeight.value = height;
        updateDimensions();
    }

    /**
     * Reset to responsive mode
     */
    function resetToResponsive() {
        isFixedMode.value = false;
        fixedWidth.value = null;
        fixedHeight.value = null;
        updateDimensions();
    }

    // Setup ResizeObserver on mount
    onMounted(() => {
        if (config.responsive !== false && container.value) {
            resizeObserver = new ResizeObserver((entries) => {
                // Only update if not in fixed mode
                if (!isFixedMode.value) {
                    // Use requestAnimationFrame to batch updates
                    requestAnimationFrame(updateDimensions);
                }
            });
            resizeObserver.observe(container.value);
        }

        // Initial calculation
        updateDimensions();
    });

    // Cleanup on unmount
    onUnmounted(() => {
        if (resizeObserver) {
            resizeObserver.disconnect();
            resizeObserver = null;
        }
    });

    // Watch for container changes (in case ref changes)
    watch(container, (newContainer, oldContainer) => {
        if (resizeObserver && oldContainer) {
            resizeObserver.unobserve(oldContainer);
        }
        if (resizeObserver && newContainer && config.responsive !== false) {
            resizeObserver.observe(newContainer);
        }
        updateDimensions();
    });

    // Watch for config changes that affect dimensions
    watch(
        () => config.aspectRatio,
        () => {
            if (!isFixedMode.value) {
                updateDimensions();
            }
        }
    );

    return {
        dimensions,
        updateDimensions,
        setFixedDimensions,
        resetToResponsive
    };
}
