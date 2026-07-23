import {describe, expect, it} from "vitest";

import {bandwidthPlotData} from "@/utils/bandwidth";

function topography(id: number, lower: number, upper: number, extra: any = {}) {
    return {
        id: id,
        name: `topo-${id}`,
        bandwidth_lower: lower,
        bandwidth_upper: upper,
        short_reliability_cutoff: null,
        thumbnail: null,
        ...extra
    };
}

describe("bandwidthPlotData", () => {
    it("skips null entries", () => {
        const data = bandwidthPlotData([null, topography(1, 1e-9, 1e-6), null]);
        expect(data.left).toEqual([1e-9]);
        expect(data.right).toEqual([1e-6]);
        expect(data.name).toEqual(["topo-1"]);
    });

    it("stacks bars ordered by lower bandwidth", () => {
        const data = bandwidthPlotData([
            topography(1, 1e-6, 1e-3),   // largest lower bound -> top
            topography(2, 1e-9, 1e-6),   // smallest lower bound -> bottom
            topography(3, 1e-8, 1e-5)
        ]);
        expect(data.y).toEqual([2, 0, 1]);
    });

    it("extracts thumbnails and links", () => {
        const data = bandwidthPlotData([
            topography(7, 1e-9, 1e-6, {thumbnail: {file: "http://x/thumb.png"}}),
            topography(8, 1e-9, 1e-6)
        ]);
        expect(data.thumbnail).toEqual(["http://x/thumb.png", null]);
        expect(data.link).toEqual(["/ui/topography/7/", "/ui/topography/8/"]);
    });
});
