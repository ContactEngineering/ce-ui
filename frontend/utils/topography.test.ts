import {describe, expect, it} from "vitest";

import {emptyTopography, filterTopographyForPatchRequest} from "@/utils/topography";

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
