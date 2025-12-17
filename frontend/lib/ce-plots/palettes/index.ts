/**
 * ce-plots/palettes - Color palettes and utilities
 */

// Continuous palettes
export { PLASMA_256 } from './plasma';
export { VIRIDIS_256 } from './viridis';
export { GREYS_256 } from './greys';

// Categorical palettes
export {
    CATEGORY_10,
    CATEGORY_20,
    TABLEAU_10,
    COLORBLIND_8
} from './categorical';

// Utilities
export {
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
} from './utils';

export type { ColorPalette } from './utils';
