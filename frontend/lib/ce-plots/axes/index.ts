/**
 * ce-plots/axes - Axis components and utilities
 */

// Components
export { default as XAxis } from './XAxis.vue';
export { default as YAxis } from './YAxis.vue';

// Composables
export { useAxisTicks } from './useAxisTicks';
export type { TickInfo, UseAxisTicksOptions, UseAxisTicksReturn } from './useAxisTicks';

// Formatters
export {
    formatExponential,
    formatExponentialHtml,
    formatSIPrefix,
    formatCompact,
    createTickFormatter
} from './formatters';
