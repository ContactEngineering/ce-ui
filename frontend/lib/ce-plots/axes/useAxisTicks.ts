/**
 * useAxisTicks - Composable for generating axis ticks
 *
 * Handles:
 * - Tick value generation for linear and log scales
 * - Tick formatting
 * - Grid line positions
 */

import { computed, type ComputedRef } from 'vue';
import type { NumericScale, AxisConfig } from '../types';
import { createTickFormatter } from './formatters';

export interface TickInfo {
    /** The tick value */
    value: number;
    /** Position in pixels */
    position: number;
    /** Formatted label string */
    label: string;
    /** Whether this is a major tick (for log scales) */
    isMajor: boolean;
}

export interface UseAxisTicksOptions {
    /** The D3 scale to use */
    scale: ComputedRef<NumericScale>;
    /** Axis configuration */
    config: AxisConfig;
    /** Axis orientation (affects tick count defaults) */
    orientation: 'x' | 'y';
}

export interface UseAxisTicksReturn {
    /** Array of tick information */
    ticks: ComputedRef<TickInfo[]>;
    /** Grid line positions (same as tick positions) */
    gridLines: ComputedRef<number[]>;
}

/**
 * Determine if a value is a "nice" number for log scale major ticks
 * (powers of 10, or 1, 2, 5 times powers of 10)
 */
function isNiceLogValue(value: number): boolean {
    if (value <= 0) return false;

    const log10 = Math.log10(value);
    const exponent = Math.floor(log10);
    const mantissa = value / Math.pow(10, exponent);

    // Check if mantissa is close to 1, 2, or 5
    return (
        Math.abs(mantissa - 1) < 0.001 ||
        Math.abs(mantissa - 2) < 0.001 ||
        Math.abs(mantissa - 5) < 0.001
    );
}

export function useAxisTicks(options: UseAxisTicksOptions): UseAxisTicksReturn {
    const { scale, config, orientation } = options;

    // Default tick count based on orientation
    const defaultTickCount = orientation === 'x' ? 6 : 5;

    // Create formatter
    const formatter = config.tickFormat ?? createTickFormatter('auto');

    const ticks = computed<TickInfo[]>(() => {
        const currentScale = scale.value;
        const tickCount = config.tickCount ?? defaultTickCount;

        // Get tick values from scale
        let tickValues: number[];

        // Check if this is a log scale by checking the domain
        const domain = currentScale.domain();
        const isLogScale = config.scaleType === 'log';

        if (isLogScale) {
            // For log scales, get more ticks and filter to nice values
            tickValues = currentScale.ticks(tickCount * 2);

            // Filter to only major ticks if we have too many
            if (tickValues.length > tickCount * 1.5) {
                tickValues = tickValues.filter(v => isNiceLogValue(v));
            }
        } else {
            tickValues = currentScale.ticks(tickCount);
        }

        // Convert to tick info objects
        return tickValues.map(value => ({
            value,
            position: currentScale(value),
            label: formatter(value),
            isMajor: isLogScale ? isNiceLogValue(value) : true
        }));
    });

    const gridLines = computed<number[]>(() => {
        return ticks.value.map(t => t.position);
    });

    return {
        ticks,
        gridLines
    };
}
