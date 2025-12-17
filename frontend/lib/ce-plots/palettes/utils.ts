/**
 * Color palette utilities
 *
 * Functions for working with color palettes:
 * - Get colors by index
 * - Create color scales
 * - Interpolate colors
 * - Generate gradient CSS
 */

import { scaleLinear, scaleSequential } from 'd3-scale';
import { interpolateRgb } from 'd3-interpolate';
import { rgb } from 'd3-color';

export type ColorPalette = string[];

/**
 * Get a color from a palette by index (wraps around)
 */
export function getColor(palette: ColorPalette, index: number): string {
    return palette[index % palette.length];
}

/**
 * Get a color from a continuous palette by normalized value [0, 1]
 */
export function getColorByValue(palette: ColorPalette, value: number): string {
    const clampedValue = Math.max(0, Math.min(1, value));
    const index = Math.floor(clampedValue * (palette.length - 1));
    return palette[index];
}

/**
 * Create a D3 color scale from a palette
 *
 * @param palette - Array of colors
 * @param domain - [min, max] domain values
 * @returns D3 scale function
 */
export function createColorScale(
    palette: ColorPalette,
    domain: [number, number] = [0, 1]
): (value: number) => string {
    const scale = scaleLinear<string>()
        .domain([domain[0], domain[1]])
        .range([palette[0], palette[palette.length - 1]])
        .interpolate(interpolateRgb);

    // Return a function that uses the palette directly for better color accuracy
    return (value: number) => {
        const normalized = (value - domain[0]) / (domain[1] - domain[0]);
        return getColorByValue(palette, normalized);
    };
}

/**
 * Create a discrete color scale for categorical data
 *
 * @param palette - Array of colors
 * @param categories - Array of category values
 * @returns Function mapping category to color
 */
export function createCategoricalScale<T>(
    palette: ColorPalette,
    categories: T[]
): (category: T) => string {
    const map = new Map<T, string>();

    categories.forEach((cat, i) => {
        map.set(cat, getColor(palette, i));
    });

    return (category: T) => map.get(category) ?? palette[0];
}

/**
 * Interpolate between two colors
 *
 * @param color1 - Start color (hex or rgb)
 * @param color2 - End color (hex or rgb)
 * @param t - Interpolation factor [0, 1]
 * @returns Interpolated color as hex string
 */
export function interpolateColor(color1: string, color2: string, t: number): string {
    const interpolator = interpolateRgb(color1, color2);
    return interpolator(t);
}

/**
 * Generate a CSS linear gradient from a palette
 *
 * @param palette - Array of colors
 * @param direction - CSS gradient direction (default: 'to right')
 * @returns CSS linear-gradient string
 */
export function paletteToGradient(
    palette: ColorPalette,
    direction: string = 'to right'
): string {
    const stops = palette.map((color, i) => {
        const percent = (i / (palette.length - 1)) * 100;
        return `${color} ${percent.toFixed(1)}%`;
    });

    return `linear-gradient(${direction}, ${stops.join(', ')})`;
}

/**
 * Sample colors from a palette at regular intervals
 *
 * @param palette - Source palette
 * @param count - Number of colors to sample
 * @returns Array of sampled colors
 */
export function samplePalette(palette: ColorPalette, count: number): string[] {
    if (count <= 0) return [];
    if (count === 1) return [palette[Math.floor(palette.length / 2)]];
    if (count >= palette.length) return [...palette];

    const result: string[] = [];
    for (let i = 0; i < count; i++) {
        const index = Math.floor((i / (count - 1)) * (palette.length - 1));
        result.push(palette[index]);
    }
    return result;
}

/**
 * Reverse a color palette
 */
export function reversePalette(palette: ColorPalette): ColorPalette {
    return [...palette].reverse();
}

/**
 * Adjust color brightness
 *
 * @param color - Hex color string
 * @param factor - Brightness factor (< 1 = darker, > 1 = lighter)
 * @returns Adjusted hex color
 */
export function adjustBrightness(color: string, factor: number): string {
    const c = rgb(color);
    c.r = Math.min(255, Math.max(0, c.r * factor));
    c.g = Math.min(255, Math.max(0, c.g * factor));
    c.b = Math.min(255, Math.max(0, c.b * factor));
    return c.formatHex();
}

/**
 * Adjust color opacity
 *
 * @param color - Hex color string
 * @param opacity - Opacity value [0, 1]
 * @returns RGBA color string
 */
export function adjustOpacity(color: string, opacity: number): string {
    const c = rgb(color);
    c.opacity = Math.min(1, Math.max(0, opacity));
    return c.formatRgb();
}

/**
 * Check if a color is "light" (for determining text contrast)
 *
 * @param color - Hex color string
 * @returns true if the color is light
 */
export function isLightColor(color: string): boolean {
    const c = rgb(color);
    // Using relative luminance formula
    const luminance = (0.299 * c.r + 0.587 * c.g + 0.114 * c.b) / 255;
    return luminance > 0.5;
}

/**
 * Get a contrasting text color (black or white) for a background
 *
 * @param backgroundColor - Background color
 * @returns '#000000' or '#ffffff'
 */
export function getContrastColor(backgroundColor: string): string {
    return isLightColor(backgroundColor) ? '#000000' : '#ffffff';
}

/**
 * Generate N distinct colors using golden ratio distribution
 * Useful for dynamic series where palette might run out
 *
 * @param count - Number of colors to generate
 * @param saturation - Color saturation [0, 100]
 * @param lightness - Color lightness [0, 100]
 * @returns Array of hex colors
 */
export function generateDistinctColors(
    count: number,
    saturation: number = 70,
    lightness: number = 50
): string[] {
    const colors: string[] = [];
    const goldenRatio = 0.618033988749895;
    let hue = Math.random();

    for (let i = 0; i < count; i++) {
        hue = (hue + goldenRatio) % 1;
        colors.push(`hsl(${Math.floor(hue * 360)}, ${saturation}%, ${lightness}%)`);
    }

    return colors;
}
