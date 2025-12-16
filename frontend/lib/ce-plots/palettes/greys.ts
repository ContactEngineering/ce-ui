/**
 * Greys colormap (256 colors)
 *
 * A grayscale colormap from white to black.
 */

// Generate 256 shades of grey from white (255) to black (0)
function generateGreys(): string[] {
    const colors: string[] = [];
    for (let i = 0; i < 256; i++) {
        // Go from white (255) to black (0)
        const value = 255 - i;
        const hex = value.toString(16).padStart(2, '0');
        colors.push(`#${hex}${hex}${hex}`);
    }
    return colors;
}

export const GREYS_256: string[] = generateGreys();

export default GREYS_256;
