/**
 * Pure helpers for organizing plot data sources into selectable categories
 * with assigned colors and line styles (used by the BokehPlot component).
 */

export interface Category {
    /** Name of the data-source key that defines this category, e.g. "seriesName". */
    key: string;
    /** Human-readable title, e.g. "Data series". */
    title: string;
}

export interface CategoryElement {
    title: string;
    color: string | null;
    dash: string | null;
    /** Whether this element is a child of another element (e.g. a measurement of a surface). */
    hasParent: boolean;
    /** Initial visibility of the data sources belonging to this element. */
    visible: boolean;
}

export const DASHES = ['solid', 'dashed', 'dotted', 'dotdash', 'dashdot'];

/**
 * For each category, create the list of unique elements found in the data
 * sources. For a category with key "seriesName", each data source must carry
 * `seriesName` (the element title), `seriesNameIndex` (its position in the
 * element list) and optionally `seriesNameHasParent`.
 */
export function buildCategoryElements(categories: Category[], dataSources: any[]): CategoryElement[][] {
    return categories.map(category => {
        const elements: CategoryElement[] = [];
        for (const dataSource of dataSources) {
            if (!(category.key in dataSource)) {
                throw new Error(`Key '${category.key}' not found in data source '${dataSource.name}'.`);
            }

            const elementIndex = dataSource[category.key + 'Index'];

            // Skip if this element has been seen before
            if (elements[elementIndex] != null) continue;

            const hasParent = dataSource[category.key + 'HasParent'];
            elements[elementIndex] = {
                title: dataSource[category.key],
                color: null,
                dash: null,
                hasParent: hasParent == null ? false : hasParent,
                // Default to showing a data source if it has no 'visible' attribute
                visible: dataSource.visible == null || dataSource.visible
            };
        }
        return elements;
    });
}

/**
 * Assign colors to the elements of the first category. Parent elements
 * (surfaces) are colored from `parentPalette`, child elements (measurements)
 * from `childPalette`; if there are no children, parents also use
 * `childPalette`.
 */
export function assignElementColors(elements: CategoryElement[],
                                    parentPalette: readonly string[],
                                    childPalette: readonly string[]): void {
    const nbChildren = elements.filter(e => e.hasParent).length;
    const nbParents = elements.length - nbChildren;

    let parentIndex = 0;
    let childIndex = 0;
    for (const element of elements) {
        if (element.hasParent) {
            element.color = childPalette[Math.trunc(childIndex * childPalette.length / nbChildren)];
            childIndex++;
        } else {
            const palette = nbChildren === 0 ? childPalette : parentPalette;
            element.color = palette[Math.trunc(parentIndex * palette.length / nbParents)];
            parentIndex++;
        }
    }
}

/**
 * Assign line styles to the elements of the second category, cycling through
 * the available dash patterns.
 */
export function assignElementDashes(elements: CategoryElement[],
                                    dashes: readonly string[] = DASHES): void {
    for (const [elementIndex, element] of elements.entries()) {
        element.dash = dashes[elementIndex % dashes.length];
    }
}

/**
 * Find a label for the legend of a plot. Data sources can carry an explicit
 * `legendLabel`; otherwise the value of the first category is used, with
 * child elements prefixed to indicate nesting.
 *
 * Note: It is not solved yet to get the legend items in the correct order to
 * display sublevels only for the correct data series and not for others, and
 * at the same time have the same colors and dashes for same subjects over
 * different analysis functions. We therefore only prefix by the first
 * category.
 */
export function legendLabel(dataSource: any, categories: Category[]): string {
    if (dataSource.legendLabel != null) {
        return dataSource.legendLabel;
    }
    if (categories.length === 0) {
        return dataSource.source_name;
    }
    let label = dataSource[categories[0].key];
    if (dataSource.hasParent === true) {
        label = "└─ " + label;
    }
    return label;
}
