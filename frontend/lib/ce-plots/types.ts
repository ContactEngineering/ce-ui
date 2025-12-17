/**
 * ce-plots - A Vue.js plotting library based on D3.js
 * Type definitions
 */

import type { ScaleLinear, ScaleLogarithmic } from 'd3-scale';

// ============================================================================
// Layout & Dimensions
// ============================================================================

export interface PlotMargins {
    top: number;
    right: number;
    bottom: number;
    left: number;
}

export interface PlotDimensions {
    width: number;
    height: number;
    innerWidth: number;   // width - margins.left - margins.right
    innerHeight: number;  // height - margins.top - margins.bottom
    margins: PlotMargins;
}

// ============================================================================
// Scales & Axes
// ============================================================================

export type ScaleType = 'linear' | 'log';

export type NumericScale = ScaleLinear<number, number> | ScaleLogarithmic<number, number>;

export interface AxisConfig {
    /** Axis label text */
    label?: string;
    /** Scale type: 'linear' or 'log' */
    scaleType?: ScaleType;
    /** Fixed domain [min, max]. If not provided, auto-calculated from data */
    domain?: [number, number];
    /** Custom tick formatter function */
    tickFormat?: (value: number) => string;
    /** Approximate number of ticks */
    tickCount?: number;
    /** Whether to show grid lines */
    showGrid?: boolean;
}

// ============================================================================
// Plot Configuration
// ============================================================================

export interface PlotConfig {
    /** X-axis configuration */
    xAxis: AxisConfig;
    /** Y-axis configuration */
    yAxis: AxisConfig;
    /** Custom margins (merged with defaults) */
    margins?: Partial<PlotMargins>;
    /** Aspect ratio (width / height). If set, height is calculated from width */
    aspectRatio?: number;
    /** Whether plot should resize with container (default: true) */
    responsive?: boolean;
    /** Minimum width in pixels */
    minWidth?: number;
    /** Minimum height in pixels */
    minHeight?: number;
}

// ============================================================================
// Data Types
// ============================================================================

export interface DataPoint {
    x: number;
    y: number;
    /** Additional fields for tooltips, selection, etc. */
    [key: string]: any;
}

export type SymbolType = 'circle' | 'x' | 'square' | 'triangle' | 'diamond';

export type DashType = 'solid' | 'dashed' | 'dotted' | 'dotdash' | 'dashdot';

export interface DataSeries {
    /** Unique identifier for this series */
    id: string;
    /** Display name (used in legend, tooltips) */
    name: string;
    /** Data points */
    data: DataPoint[];
    /** Line/fill color (CSS color string) */
    color?: string;
    /** Line dash pattern */
    dash?: DashType;
    /** Line width in pixels */
    lineWidth?: number;
    /** Symbol type for scatter points */
    symbol?: SymbolType;
    /** Symbol size in pixels */
    symbolSize?: number;
    /** Opacity (0-1) */
    opacity?: number;
    /** Whether this series is visible */
    visible?: boolean;
    /** Whether this is a child series (affects default color palette) */
    isChild?: boolean;
    /** Index within category (for color assignment) */
    categoryIndex?: number;
}

// ============================================================================
// Interaction State
// ============================================================================

export interface SelectionState {
    /** ID of selected series, or null if nothing selected */
    seriesId: string | null;
    /** Index of selected point within series, or null */
    pointIndex: number | null;
}

export interface ZoomTransform {
    /** X translation */
    x: number;
    /** Y translation */
    y: number;
    /** Scale factor (1 = no zoom) */
    k: number;
}

export interface TooltipContext {
    /** The data point being hovered */
    point: DataPoint;
    /** The series containing the point */
    series: DataSeries;
    /** Screen X coordinate */
    screenX: number;
    /** Screen Y coordinate */
    screenY: number;
}

// ============================================================================
// Events
// ============================================================================

export interface PlotEvents {
    /** Emitted when a point is selected */
    select: [seriesId: string, pointIndex: number, point: DataPoint];
    /** Emitted when selection is cleared */
    deselect: [];
    /** Emitted when zoom/pan changes */
    zoom: [transform: ZoomTransform];
    /** Emitted when zoom is reset */
    zoomReset: [];
}

// ============================================================================
// Data Loading
// ============================================================================

export interface DataLoaderOptions {
    /** URL to fetch data from */
    url: string;
    /** Field name or extractor function for X values */
    xField?: string | ((data: any) => number[]);
    /** Field name or extractor function for Y values */
    yField?: string | ((data: any) => number[]);
    /** Scale factor to apply to X values */
    xScaleFactor?: number;
    /** Scale factor to apply to Y values */
    yScaleFactor?: number;
    /** Custom transform function for raw data */
    transform?: (data: any) => DataPoint[];
    /** Additional fields to extract for each point */
    auxiliaryFields?: Record<string, string | ((data: any, index: number) => any)>;
}

// ============================================================================
// Export Options
// ============================================================================

export interface ExportOptions {
    /** Filename (without extension) */
    filename?: string;
    /** Scale factor for PNG export (default: 2 for retina) */
    scale?: number;
    /** Background color (default: white) */
    backgroundColor?: string;
}

// ============================================================================
// Theme & Styling
// ============================================================================

export interface PlotTheme {
    /** Font family for labels and ticks */
    fontFamily: string;
    /** Font size for axis labels */
    labelFontSize: number;
    /** Font size for tick labels */
    tickFontSize: number;
    /** Color for axis lines and ticks */
    axisColor: string;
    /** Color for grid lines */
    gridColor: string;
    /** Grid line opacity */
    gridOpacity: number;
    /** Default line width */
    defaultLineWidth: number;
    /** Default symbol size */
    defaultSymbolSize: number;
    /** Default opacity */
    defaultOpacity: number;
}

export const DEFAULT_THEME: PlotTheme = {
    fontFamily: 'system-ui, -apple-system, sans-serif',
    labelFontSize: 14,
    tickFontSize: 12,
    axisColor: '#333',
    gridColor: '#e0e0e0',
    gridOpacity: 0.7,
    defaultLineWidth: 1.5,
    defaultSymbolSize: 8,
    defaultOpacity: 1
};

export const DEFAULT_MARGINS: PlotMargins = {
    top: 20,
    right: 30,
    bottom: 50,
    left: 60
};
