import {describe, expect, it} from "vitest";

import {describeDetrend, emptyTopography, filterTopographyForPatchRequest} from "@/utils/topography";

describe("emptyTopography", () => {
    it("has no server-side representation and no data", () => {
        const t = emptyTopography();
        expect(t.url).toBeNull();
        expect(t.name).toBeNull();
        expect(t.tags).toEqual([]);
        expect(t.size_editable).toBe(true);
        expect(t.unit_editable).toBe(true);
        expect(t.height_scale_editable).toBe(true);
    });

    it("yields an empty patch", () => {
        expect(filterTopographyForPatchRequest(emptyTopography())).toEqual({tags: []});
    });
});

describe("filterTopographyForPatchRequest", () => {
    it("keeps writable non-null entries and drops everything else", () => {
        const patch = filterTopographyForPatchRequest({
            url: "/manager/api/topography/1/",  // not writable
            name: "measurement",
            description: null,  // null entries are dropped
            thumbnail: "abc",  // not writable
            detrend_mode: "center"
        });
        expect(patch).toEqual({name: "measurement", detrend_mode: "center"});
    });

    it("honors editability flags", () => {
        const topography = {
            size_x: 1,
            size_y: 2,
            unit: "nm",
            height_scale: 1.5,
            is_periodic: true,
            size_editable: false,
            unit_editable: false,
            height_scale_editable: false,
            is_periodic_editable: false
        };
        expect(filterTopographyForPatchRequest(topography)).toEqual({});
        expect(filterTopographyForPatchRequest({
            ...topography,
            size_editable: true,
            unit_editable: true,
            height_scale_editable: true,
            is_periodic_editable: true
        })).toEqual({
            size_x: 1,
            size_y: 2,
            unit: "nm",
            height_scale: 1.5,
            is_periodic: true
        });
    });
});

describe("describeDetrend", () => {
    it("names the slope in each lateral direction", () => {
        expect(describeDetrend({slope_x: 0.0025, slope_y: 0.0071}, "µm"))
            .toBe("slope 0.0025 in x, slope 0.0071 in y");
    });

    it("names the radius with the lateral unit", () => {
        expect(describeDetrend({slope_x: 0.5, radius_x: 50}, "µm"))
            .toBe("slope 0.5 in x, radius 50 µm in x");
    });

    it("switches to exponential notation below a thousandth", () => {
        expect(describeDetrend({slope_x: 2.5e-7}, "µm")).toBe("slope 2.5×10⁻⁷ in x");
    });

    it("omits what the fit does not determine", () => {
        // A line scan has no y component, and a flat direction has no radius
        expect(describeDetrend({slope_x: 0.5}, "µm")).toBe("slope 0.5 in x");
    });

    it("has no description when no trend was fitted", () => {
        // A mode that only subtracts the mean
        expect(describeDetrend({}, "µm")).toBeNull();
    });

    it("has no description for a measurement that has not been inspected", () => {
        expect(describeDetrend(null, "µm")).toBeNull();
        expect(describeDetrend(undefined, "µm")).toBeNull();
    });

    it("leaves the unit off when the measurement has none", () => {
        expect(describeDetrend({radius_x: 50}, null)).toBe("radius 50 in x");
    });
});
