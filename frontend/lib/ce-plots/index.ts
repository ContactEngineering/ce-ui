/**
 * ce-plots - A Vue.js plotting library based on D3.js
 *
 * @example
 * ```vue
 * <template>
 *   <Plot :config="config" :series="series">
 *     <template #axes>
 *       <XAxis :config="config.xAxis" />
 *       <YAxis :config="config.yAxis" />
 *     </template>
 *     <Line v-for="s in series" :key="s.id" :series="s" />
 *     <Scatter v-for="s in series" :key="s.id" :series="s" />
 *   </Plot>
 * </template>
 *
 * <script setup>
 * import { Plot, XAxis, YAxis, Line, Scatter } from '@/lib/ce-plots';
 * </script>
 * ```
 */

// =============================================================================
// Types
// =============================================================================

export type {
    // Layout
    PlotMargins,
    PlotDimensions,

    // Scales
    ScaleType,
    NumericScale,
    AxisConfig,

    // Configuration
    PlotConfig,

    // Data
    DataPoint,
    SymbolType,
    DashType,
    DataSeries,

    // Interaction
    SelectionState,
    ZoomTransform,
    TooltipContext,

    // Events
    PlotEvents,

    // Data loading
    DataLoaderOptions,

    // Export
    ExportOptions,

    // Theme
    PlotTheme
} from './types';

export { DEFAULT_THEME, DEFAULT_MARGINS } from './types';

// =============================================================================
// Core
// =============================================================================

export {
    // Components
    Plot,

    // Context
    PlotContextKey,
    usePlotContext,

    // Composables
    usePlotDimensions,
    usePlotScales,
    usePlotTransform
} from './core';

export type {
    PlotContext,
    UsePlotDimensionsOptions,
    UsePlotDimensionsReturn,
    UsePlotScalesOptions,
    UsePlotScalesReturn,
    UsePlotTransformOptions,
    UsePlotTransformReturn
} from './core';

// =============================================================================
// Axes
// =============================================================================

export {
    // Components
    XAxis,
    YAxis,

    // Composables
    useAxisTicks,

    // Formatters
    formatExponential,
    formatExponentialHtml,
    formatSIPrefix,
    formatCompact,
    createTickFormatter
} from './axes';

export type {
    TickInfo,
    UseAxisTicksOptions,
    UseAxisTicksReturn
} from './axes';

// =============================================================================
// Glyphs
// =============================================================================

export {
    Line,
    Scatter,
    HBar
} from './glyphs';

export type {
    HBarDataPoint
} from './glyphs';

// =============================================================================
// Interactions
// =============================================================================

export {
    // Components
    Tooltip,

    // Composables
    useTooltip,
    useSelection
} from './interactions';

export type {
    UseTooltipOptions,
    UseTooltipReturn,
    UseSelectionOptions,
    UseSelectionReturn
} from './interactions';

// =============================================================================
// Legend
// =============================================================================

export {
    Legend,
    LegendItem
} from './legend';

export type {
    LegendGroup
} from './legend';

// =============================================================================
// Data Loading
// =============================================================================

export {
    useDataLoader
} from './data';

export type {
    LoadedData,
    UseDataLoaderOptions,
    UseDataLoaderReturn
} from './data';

// =============================================================================
// Export
// =============================================================================

export {
    useExport,
    ExportButton
} from './export';

export type {
    UseExportOptions,
    UseExportReturn
} from './export';

// =============================================================================
// Color Palettes
// =============================================================================

export {
    // Continuous palettes
    PLASMA_256,
    VIRIDIS_256,
    GREYS_256,

    // Categorical palettes
    CATEGORY_10,
    CATEGORY_20,
    TABLEAU_10,
    COLORBLIND_8,

    // Utilities
    getColor,
    getColorByValue,
    createColorScale,
    createCategoricalScale,
    interpolateColor,
    paletteToGradient,
    samplePalette,
    reversePalette,
    adjustBrightness,
    adjustOpacity,
    isLightColor,
    getContrastColor,
    generateDistinctColors
} from './palettes';

export type { ColorPalette } from './palettes';
