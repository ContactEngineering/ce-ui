/**
 * usePlotScales - Composable for D3 scale management
 *
 * Handles:
 * - Linear and logarithmic scales
 * - Auto-domain calculation from data
 * - Zoom transform application
 * - Scale updates when data or dimensions change
 */

import { computed, type Ref, type ComputedRef } from 'vue';
import { scaleLinear, scaleLog } from 'd3-scale';
import { extent } from 'd3-array';
import type {
    PlotConfig,
    PlotDimensions,
    DataSeries,
    ZoomTransform,
    NumericScale
} from '../types';

export interface UsePlotScalesOptions {
    /** Plot configuration */
    config: PlotConfig;
    /** Reactive dimensions */
    dimensions: Ref<PlotDimensions>;
    /** Data series for auto-domain calculation */
    series: Ref<DataSeries[]>;
    /** Current zoom transform */
    transform: Ref<ZoomTransform>;
}

export interface UsePlotScalesReturn {
    /** X scale with zoom transform applied */
    xScale: ComputedRef<NumericScale>;
    /** Y scale with zoom transform applied */
    yScale: ComputedRef<NumericScale>;
    /** Original X scale without zoom (for axes) */
    xScaleOriginal: ComputedRef<NumericScale>;
    /** Original Y scale without zoom (for axes) */
    yScaleOriginal: ComputedRef<NumericScale>;
    /** Current X domain */
    xDomain: ComputedRef<[number, number]>;
    /** Current Y domain */
    yDomain: ComputedRef<[number, number]>;
}

/**
 * Calculate domain from data series
 */
function calculateDomain(
    series: DataSeries[],
    accessor: (point: { x: number; y: number }) => number,
    fixedDomain?: [number, number]
): [number, number] {
    if (fixedDomain) {
        return fixedDomain;
    }

    // Get all visible data points
    const visibleSeries = series.filter(s => s.visible !== false);
    const allValues = visibleSeries.flatMap(s => s.data.map(accessor));

    if (allValues.length === 0) {
        return [0, 1]; // Default domain when no data
    }

    const [min, max] = extent(allValues) as [number, number];

    // Handle edge case where all values are the same
    if (min === max) {
        if (min === 0) {
            return [-1, 1];
        }
        // Add 10% padding on each side
        const padding = Math.abs(min) * 0.1;
        return [min - padding, max + padding];
    }

    return [min, max];
}

/**
 * Add padding to domain for nicer axis bounds
 */
function padDomain(domain: [number, number], scaleType: 'linear' | 'log', padding: number = 0.05): [number, number] {
    const [min, max] = domain;

    if (scaleType === 'log') {
        // For log scales, padding is multiplicative
        // Also ensure domain doesn't include zero or negative
        const safeMin = min > 0 ? min : 1e-10;
        const safeMax = max > 0 ? max : 1;
        const ratio = safeMax / safeMin;
        const paddingFactor = Math.pow(ratio, padding);
        return [safeMin / paddingFactor, safeMax * paddingFactor];
    }

    // For linear scales, padding is additive
    const range = max - min;
    const paddingAmount = range * padding;
    return [min - paddingAmount, max + paddingAmount];
}

export function usePlotScales(options: UsePlotScalesOptions): UsePlotScalesReturn {
    const { config, dimensions, series, transform } = options;

    // Calculate domains from data (reactive)
    const xDomain = computed<[number, number]>(() => {
        const domain = calculateDomain(series.value, d => d.x, config.xAxis.domain);
        return padDomain(domain, config.xAxis.scaleType ?? 'linear');
    });

    const yDomain = computed<[number, number]>(() => {
        const domain = calculateDomain(series.value, d => d.y, config.yAxis.domain);
        return padDomain(domain, config.yAxis.scaleType ?? 'linear');
    });

    // Original scales without zoom (used for axes)
    const xScaleOriginal = computed<NumericScale>(() => {
        const scale = config.xAxis.scaleType === 'log'
            ? scaleLog<number, number>()
            : scaleLinear<number, number>();

        return scale
            .domain(xDomain.value)
            .range([0, dimensions.value.innerWidth]);
    });

    const yScaleOriginal = computed<NumericScale>(() => {
        const scale = config.yAxis.scaleType === 'log'
            ? scaleLog<number, number>()
            : scaleLinear<number, number>();

        return scale
            .domain(yDomain.value)
            .range([dimensions.value.innerHeight, 0]); // Y is inverted in SVG
    });

    // Scales with zoom transform applied (used for data rendering)
    const xScale = computed<NumericScale>(() => {
        const scale = xScaleOriginal.value.copy();
        const t = transform.value;

        if (t.k !== 1 || t.x !== 0) {
            // Apply zoom transform to range
            const [r0, r1] = scale.range();
            scale.range([r0 * t.k + t.x, r1 * t.k + t.x]);
        }

        return scale;
    });

    const yScale = computed<NumericScale>(() => {
        const scale = yScaleOriginal.value.copy();
        const t = transform.value;

        if (t.k !== 1 || t.y !== 0) {
            // Apply zoom transform to range
            const [r0, r1] = scale.range();
            scale.range([r0 * t.k + t.y, r1 * t.k + t.y]);
        }

        return scale;
    });

    return {
        xScale,
        yScale,
        xScaleOriginal,
        yScaleOriginal,
        xDomain,
        yDomain
    };
}
