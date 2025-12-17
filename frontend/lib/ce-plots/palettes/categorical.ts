/**
 * Categorical color palettes
 *
 * Distinct colors for categorical data and series differentiation.
 */

/**
 * Default categorical palette (10 colors)
 * Based on D3's Category10
 */
export const CATEGORY_10: string[] = [
    '#1f77b4', // blue
    '#ff7f0e', // orange
    '#2ca02c', // green
    '#d62728', // red
    '#9467bd', // purple
    '#8c564b', // brown
    '#e377c2', // pink
    '#7f7f7f', // gray
    '#bcbd22', // olive
    '#17becf'  // cyan
];

/**
 * Extended categorical palette (20 colors)
 * Based on D3's Category20
 */
export const CATEGORY_20: string[] = [
    '#1f77b4', '#aec7e8', // blues
    '#ff7f0e', '#ffbb78', // oranges
    '#2ca02c', '#98df8a', // greens
    '#d62728', '#ff9896', // reds
    '#9467bd', '#c5b0d5', // purples
    '#8c564b', '#c49c94', // browns
    '#e377c2', '#f7b6d2', // pinks
    '#7f7f7f', '#c7c7c7', // grays
    '#bcbd22', '#dbdb8d', // olives
    '#17becf', '#9edae5'  // cyans
];

/**
 * Tableau 10 palette
 * A refined categorical palette with better visual distinction
 */
export const TABLEAU_10: string[] = [
    '#4e79a7', // blue
    '#f28e2c', // orange
    '#e15759', // red
    '#76b7b2', // teal
    '#59a14f', // green
    '#edc949', // yellow
    '#af7aa1', // purple
    '#ff9da7', // pink
    '#9c755f', // brown
    '#bab0ab'  // gray
];

/**
 * Colorblind-safe palette (8 colors)
 * Optimized for deuteranopia and protanopia
 */
export const COLORBLIND_8: string[] = [
    '#0077bb', // blue
    '#33bbee', // cyan
    '#009988', // teal
    '#ee7733', // orange
    '#cc3311', // red
    '#ee3377', // magenta
    '#bbbbbb', // grey
    '#000000'  // black
];

export default CATEGORY_10;
