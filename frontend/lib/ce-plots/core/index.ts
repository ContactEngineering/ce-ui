/**
 * ce-plots/core - Core components and composables
 */

// Components
export { default as Plot } from './Plot.vue';

// Context
export { PlotContextKey, usePlotContext } from './PlotContext';
export type { PlotContext } from './PlotContext';

// Composables
export { usePlotDimensions } from './usePlotDimensions';
export type { UsePlotDimensionsOptions, UsePlotDimensionsReturn } from './usePlotDimensions';

export { usePlotScales } from './usePlotScales';
export type { UsePlotScalesOptions, UsePlotScalesReturn } from './usePlotScales';

export { usePlotTransform } from './usePlotTransform';
export type { UsePlotTransformOptions, UsePlotTransformReturn } from './usePlotTransform';
