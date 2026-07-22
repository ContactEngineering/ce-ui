import {describe, expect, it} from "vitest";

import {
    assignElementColors,
    assignElementDashes,
    buildCategoryElements,
    DASHES,
    legendLabel
} from "@/utils/plot";

const categories = [
    {key: "subjectName", title: "Measurements"},
    {key: "seriesName", title: "Data series"}
];

function dataSource(subject: string, subjectIndex: number, series: string, seriesIndex: number, extra: any = {}) {
    return {
        subjectName: subject,
        subjectNameIndex: subjectIndex,
        seriesName: series,
        seriesNameIndex: seriesIndex,
        ...extra
    };
}

describe("buildCategoryElements", () => {
    it("creates unique elements per category", () => {
        const elements = buildCategoryElements(categories, [
            dataSource("topo-1", 0, "1D PSD", 0),
            dataSource("topo-1", 0, "2D PSD", 1),
            dataSource("topo-2", 1, "1D PSD", 0)
        ]);
        expect(elements).toHaveLength(2);
        expect(elements[0].map(e => e.title)).toEqual(["topo-1", "topo-2"]);
        expect(elements[1].map(e => e.title)).toEqual(["1D PSD", "2D PSD"]);
    });

    it("defaults to visible elements without parents", () => {
        const [elements] = buildCategoryElements([categories[0]], [
            dataSource("topo-1", 0, "1D PSD", 0)
        ]);
        expect(elements[0].visible).toBe(true);
        expect(elements[0].hasParent).toBe(false);
    });

    it("respects visibility and parent flags", () => {
        const [elements] = buildCategoryElements([categories[0]], [
            dataSource("surf-1", 0, "1D PSD", 0),
            dataSource("topo-1", 1, "1D PSD", 0, {subjectNameHasParent: true, visible: false})
        ]);
        expect(elements[0].hasParent).toBe(false);
        expect(elements[1].hasParent).toBe(true);
        expect(elements[1].visible).toBe(false);
    });

    it("throws if a data source lacks the category key", () => {
        expect(() => buildCategoryElements(categories, [{name: "broken"}]))
            .toThrow(/subjectName/);
    });
});

describe("assignElementColors", () => {
    const parentPalette = ["p0", "p1", "p2", "p3"];
    const childPalette = ["c0", "c1", "c2", "c3"];

    it("uses the child palette for all elements if there are no children", () => {
        const [elements] = buildCategoryElements([categories[0]], [
            dataSource("topo-1", 0, "s", 0),
            dataSource("topo-2", 1, "s", 0)
        ]);
        assignElementColors(elements, parentPalette, childPalette);
        expect(elements.map(e => e.color)).toEqual(["c0", "c2"]);
    });

    it("colors parents and children from separate palettes", () => {
        const [elements] = buildCategoryElements([categories[0]], [
            dataSource("surf-1", 0, "s", 0),
            dataSource("topo-1", 1, "s", 0, {subjectNameHasParent: true})
        ]);
        assignElementColors(elements, parentPalette, childPalette);
        expect(elements[0].color).toBe("p0");
        expect(elements[1].color).toBe("c0");
    });
});

describe("assignElementDashes", () => {
    it("cycles through the dash patterns", () => {
        const elements = Array.from({length: DASHES.length + 1}, (_, i) => ({
            title: `e${i}`, color: null, dash: null, hasParent: false, visible: true
        }));
        assignElementDashes(elements);
        expect(elements[0].dash).toBe("solid");
        expect(elements[1].dash).toBe("dashed");
        expect(elements[DASHES.length].dash).toBe("solid");
    });
});

describe("legendLabel", () => {
    it("prefers an explicit legend label", () => {
        expect(legendLabel({legendLabel: "custom", source_name: "src"}, categories)).toBe("custom");
    });

    it("falls back to the source name without categories", () => {
        expect(legendLabel({source_name: "src"}, [])).toBe("src");
    });

    it("uses the first category value and marks children", () => {
        expect(legendLabel(dataSource("topo-1", 0, "s", 0), categories)).toBe("topo-1");
        expect(legendLabel(dataSource("topo-1", 0, "s", 0, {hasParent: true}), categories))
            .toBe("└─ topo-1");
    });
});
