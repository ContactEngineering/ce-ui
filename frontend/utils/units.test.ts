import {describe, expect, it} from "vitest";

import {maxAbsolute, rescaleLengthUnit} from "@/utils/units";

/** Scale `magnitude` the way a caller would, to check the tick value it yields. */
function scaled(magnitude: number, unit: string | null): { value: number, unit: string } {
    const {unit: to, factor} = rescaleLengthUnit(magnitude, unit);
    return {value: magnitude * factor, unit: to};
}

describe("rescaleLengthUnit", () => {
    it("scales into the unit that needs no exponent", () => {
        expect(scaled(2.5e-6, "m")).toEqual({value: 2.5, unit: "µm"});
        expect(scaled(2.5e-9, "m")).toEqual({value: 2.5, unit: "nm"});
        expect(scaled(1.2e4, "m")).toEqual({value: 12, unit: "km"});
    });

    it("scales between two non-metre units", () => {
        expect(scaled(2500, "nm")).toEqual({value: 2.5, unit: "µm"});
        expect(scaled(0.002, "mm")).toEqual({value: 2, unit: "µm"});
    });

    it("accepts ångström as input but never picks it for display", () => {
        expect(scaled(50, "Å")).toEqual({value: 5, unit: "nm"});
        expect(scaled(50000, "Å")).toEqual({value: 5, unit: "µm"});
    });

    it("accepts the ascii spelling of micrometres", () => {
        expect(rescaleLengthUnit(1, "um").unit).toBe("µm");
    });

    it("keeps every tick value in [1, 1000)", () => {
        // Walk the decades either side of the common range and confirm the
        // scaled magnitude never needs an exponent.
        for (let e = -15; e <= 9; e++) {
            const {value} = scaled(Math.pow(10, e), "m");
            expect(value).toBeGreaterThanOrEqual(1);
            expect(value).toBeLessThan(1000);
        }
    });

    it("switches unit exactly at the thousand boundary", () => {
        expect(scaled(999, "nm").unit).toBe("nm");
        expect(scaled(1000, "nm")).toEqual({value: 1, unit: "µm"});
    });

    it("clamps beyond the largest and smallest known unit", () => {
        expect(rescaleLengthUnit(1e30, "m").unit).toBe("Gm");
        expect(rescaleLengthUnit(1e-30, "m").unit).toBe("fm");
    });

    it("passes through units it does not know", () => {
        expect(rescaleLengthUnit(1e-6, "V")).toEqual({unit: "V", factor: 1});
        expect(rescaleLengthUnit(1e-6, null)).toEqual({unit: null, factor: 1});
        expect(rescaleLengthUnit(1e-6, undefined)).toEqual({unit: undefined, factor: 1});
    });

    it("passes through magnitudes that imply no scale", () => {
        expect(rescaleLengthUnit(0, "m")).toEqual({unit: "m", factor: 1});
        expect(rescaleLengthUnit(NaN, "m")).toEqual({unit: "m", factor: 1});
        expect(rescaleLengthUnit(Infinity, "m")).toEqual({unit: "m", factor: 1});
    });

    it("ignores the sign of the magnitude", () => {
        expect(rescaleLengthUnit(-2.5e-6, "m")).toEqual(rescaleLengthUnit(2.5e-6, "m"));
    });
});

describe("rescaleLengthUnit on realistic line scans", () => {
    // A 100 µm long scan with 50 nm of roughness: the two axes must land on
    // different units, which is the whole point of scaling them separately.
    it("separates position and height for a scan stored in metres", () => {
        expect(scaled(1e-4, "m")).toEqual({value: 100, unit: "µm"});
        expect(scaled(5e-8, "m")).toEqual({value: 50, unit: "nm"});
    });

    it("separates position and height for the same scan stored in µm", () => {
        expect(scaled(100, "µm")).toEqual({value: 100, unit: "µm"});
        expect(scaled(0.05, "µm")).toEqual({value: 50, unit: "nm"});
    });

    // Picometres are the native unit of VK files, so data arrives with very
    // large numbers that need scaling down rather than up.
    it("scales down a scan stored in picometres", () => {
        expect(scaled(1e8, "pm")).toEqual({value: 100, unit: "µm"});
    });
});

describe("maxAbsolute", () => {
    it("returns the largest absolute value", () => {
        expect(maxAbsolute([1, -5, 3])).toBe(5);
        expect(maxAbsolute([-1, -2])).toBe(2);
    });

    it("skips undefined data points and empty input", () => {
        expect(maxAbsolute([1, NaN, 3])).toBe(3);
        expect(maxAbsolute([NaN, Infinity])).toBe(0);
        expect(maxAbsolute([])).toBe(0);
    });

    it("works on typed arrays", () => {
        expect(maxAbsolute(new Float64Array([1, -7, 2]))).toBe(7);
    });
});
