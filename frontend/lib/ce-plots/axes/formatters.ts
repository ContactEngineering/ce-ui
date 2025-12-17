/**
 * Axis tick formatters
 *
 * Provides formatting functions for axis tick labels including:
 * - Exponential notation (1.5×10³)
 * - SI prefixes (1.5 kHz)
 * - Compact notation
 */

/**
 * Format a number using exponential notation with Unicode superscripts
 * Example: 1500 → "1.5×10³", 0.00015 → "1.5×10⁻⁴"
 *
 * @param value - The number to format
 * @param precision - Number of significant digits (default: 2)
 * @returns Formatted string
 */
export function formatExponential(value: number, precision: number = 2): string {
    if (value === 0) return '0';
    if (!isFinite(value)) return String(value);

    const absValue = Math.abs(value);
    const exponent = Math.floor(Math.log10(absValue));

    // Use regular notation for small exponents
    if (exponent >= -2 && exponent <= 3) {
        // Format with appropriate decimal places
        const formatted = value.toPrecision(precision + 1);
        // Remove trailing zeros after decimal point
        return parseFloat(formatted).toString();
    }

    const mantissa = value / Math.pow(10, exponent);
    const mantissaStr = mantissa.toFixed(precision - 1);

    // Convert exponent to superscript
    const superscriptDigits: Record<string, string> = {
        '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
        '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
        '-': '⁻'
    };

    const exponentStr = String(exponent)
        .split('')
        .map(char => superscriptDigits[char] || char)
        .join('');

    return `${mantissaStr}×10${exponentStr}`;
}

/**
 * Format a number using exponential notation with HTML superscripts
 * Example: 1500 → "1.5×10<sup>3</sup>"
 *
 * @param value - The number to format
 * @param precision - Number of significant digits (default: 2)
 * @returns HTML formatted string
 */
export function formatExponentialHtml(value: number, precision: number = 2): string {
    if (value === 0) return '0';
    if (!isFinite(value)) return String(value);

    const absValue = Math.abs(value);
    const exponent = Math.floor(Math.log10(absValue));

    // Use regular notation for small exponents
    if (exponent >= -2 && exponent <= 3) {
        return parseFloat(value.toPrecision(precision + 1)).toString();
    }

    const mantissa = value / Math.pow(10, exponent);
    const mantissaStr = mantissa.toFixed(precision - 1);

    return `${mantissaStr}×10<sup>${exponent}</sup>`;
}

/**
 * SI prefix information
 */
const SI_PREFIXES: Array<{ threshold: number; prefix: string; factor: number }> = [
    { threshold: 1e24, prefix: 'Y', factor: 1e24 },   // yotta
    { threshold: 1e21, prefix: 'Z', factor: 1e21 },   // zetta
    { threshold: 1e18, prefix: 'E', factor: 1e18 },   // exa
    { threshold: 1e15, prefix: 'P', factor: 1e15 },   // peta
    { threshold: 1e12, prefix: 'T', factor: 1e12 },   // tera
    { threshold: 1e9, prefix: 'G', factor: 1e9 },     // giga
    { threshold: 1e6, prefix: 'M', factor: 1e6 },     // mega
    { threshold: 1e3, prefix: 'k', factor: 1e3 },     // kilo
    { threshold: 1, prefix: '', factor: 1 },          // base
    { threshold: 1e-3, prefix: 'm', factor: 1e-3 },   // milli
    { threshold: 1e-6, prefix: 'μ', factor: 1e-6 },   // micro
    { threshold: 1e-9, prefix: 'n', factor: 1e-9 },   // nano
    { threshold: 1e-12, prefix: 'p', factor: 1e-12 }, // pico
    { threshold: 1e-15, prefix: 'f', factor: 1e-15 }, // femto
    { threshold: 1e-18, prefix: 'a', factor: 1e-18 }, // atto
    { threshold: 1e-21, prefix: 'z', factor: 1e-21 }, // zepto
    { threshold: 1e-24, prefix: 'y', factor: 1e-24 }, // yocto
];

/**
 * Format a number using SI prefixes
 * Example: 1500 → "1.5k", 0.00015 → "150μ"
 *
 * @param value - The number to format
 * @param precision - Number of significant digits (default: 3)
 * @param unit - Optional unit to append (e.g., "Hz" → "1.5 kHz")
 * @returns Formatted string
 */
export function formatSIPrefix(value: number, precision: number = 3, unit: string = ''): string {
    if (value === 0) return `0${unit ? ' ' + unit : ''}`;
    if (!isFinite(value)) return String(value);

    const absValue = Math.abs(value);

    // Find appropriate prefix
    for (const { threshold, prefix, factor } of SI_PREFIXES) {
        if (absValue >= threshold * 0.9999) { // Small tolerance for floating point
            const scaled = value / factor;
            const formatted = parseFloat(scaled.toPrecision(precision)).toString();
            const space = unit || prefix ? ' ' : '';
            return `${formatted}${space}${prefix}${unit}`;
        }
    }

    // Fallback to exponential for very small numbers
    return formatExponential(value, precision);
}

/**
 * Format a number in compact notation
 * Similar to SI but with K, M, B, T for thousands, millions, billions, trillions
 *
 * @param value - The number to format
 * @param precision - Number of significant digits (default: 2)
 * @returns Formatted string
 */
export function formatCompact(value: number, precision: number = 2): string {
    if (value === 0) return '0';
    if (!isFinite(value)) return String(value);

    const absValue = Math.abs(value);
    const sign = value < 0 ? '-' : '';

    if (absValue >= 1e12) {
        return `${sign}${(absValue / 1e12).toPrecision(precision)}T`;
    }
    if (absValue >= 1e9) {
        return `${sign}${(absValue / 1e9).toPrecision(precision)}B`;
    }
    if (absValue >= 1e6) {
        return `${sign}${(absValue / 1e6).toPrecision(precision)}M`;
    }
    if (absValue >= 1e3) {
        return `${sign}${(absValue / 1e3).toPrecision(precision)}K`;
    }

    return parseFloat(value.toPrecision(precision)).toString();
}

/**
 * Create a D3-compatible tick formatter function
 *
 * @param format - Format type: 'exponential', 'si', 'compact', or 'auto'
 * @param options - Format options
 * @returns Formatter function
 */
export function createTickFormatter(
    format: 'exponential' | 'si' | 'compact' | 'auto' = 'auto',
    options: { precision?: number; unit?: string } = {}
): (value: number) => string {
    const { precision = 2, unit = '' } = options;

    switch (format) {
        case 'exponential':
            return (value: number) => formatExponential(value, precision);

        case 'si':
            return (value: number) => formatSIPrefix(value, precision, unit);

        case 'compact':
            return (value: number) => formatCompact(value, precision);

        case 'auto':
        default:
            // Auto-detect based on value range
            return (value: number) => {
                const absValue = Math.abs(value);
                if (absValue === 0) return '0';
                if (absValue >= 1e6 || absValue < 1e-3) {
                    return formatExponential(value, precision);
                }
                return parseFloat(value.toPrecision(precision + 1)).toString();
            };
    }
}
