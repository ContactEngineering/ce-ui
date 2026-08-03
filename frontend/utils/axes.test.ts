import {describe, expect, it} from "vitest";

import {
    parseAxisLabel,
    reciprocalLengthUnit,
    wavelengthAxis,
    wavelengthRange
} from "@/utils/axes";

describe("parseAxisLabel", () => {
    it("splits the unit off the quantity", () => {
        expect(parseAxisLabel("Wavevector (µm⁻¹)")).toEqual({quantity: "Wavevector", unit: "µm⁻¹"});
    });

    it("handles a label without a unit", () => {
        expect(parseAxisLabel("Slope")).toEqual({quantity: "Slope", unit: null});
    });

    it("handles an empty unit, which the backend writes for a dimensionless axis", () => {
        expect(parseAxisLabel("Slope ()")).toEqual({quantity: "Slope", unit: ""});
    });

    it("takes the trailing parenthesis, not an earlier one", () => {
        expect(parseAxisLabel("PSD (1D) (µm³)")).toEqual({quantity: "PSD (1D)", unit: "µm³"});
    });

    it("handles missing input", () => {
        expect(parseAxisLabel(null)).toEqual({quantity: "", unit: null});
        expect(parseAxisLabel(undefined)).toEqual({quantity: "", unit: null});
    });
});

describe("reciprocalLengthUnit", () => {
    it("recognizes the spelling the backend produces", () => {
        expect(reciprocalLengthUnit("µm⁻¹")).toBe("µm");
        expect(reciprocalLengthUnit("nm⁻¹")).toBe("nm");
        expect(reciprocalLengthUnit("m⁻¹")).toBe("m");
    });

    it("recognizes hand-written spellings", () => {
        expect(reciprocalLengthUnit("1/µm")).toBe("µm");
        expect(reciprocalLengthUnit("1 / nm")).toBe("nm");
        expect(reciprocalLengthUnit("mm^-1")).toBe("mm");
    });

    it("rejects units that are not a reciprocal length", () => {
        expect(reciprocalLengthUnit("µm")).toBeNull();
        expect(reciprocalLengthUnit("µm³")).toBeNull();
        expect(reciprocalLengthUnit("1/s")).toBeNull();
        expect(reciprocalLengthUnit("")).toBeNull();
        expect(reciprocalLengthUnit(null)).toBeNull();
    });
});

describe("wavelengthAxis", () => {
    it("adds an axis to a logarithmic wavevector axis", () => {
        expect(wavelengthAxis("Wavevector (µm⁻¹)", "log")).toEqual({
            label: "Wavelength λ = 2π/q (µm)",
            unit: "µm"
        });
    });

    it("is case-insensitive about the quantity", () => {
        expect(wavelengthAxis("wavevector (nm⁻¹)", "log")).not.toBeNull();
    });

    it("does not add one to the curvature distribution, which is also a reciprocal length", () => {
        expect(wavelengthAxis("Curvature (µm⁻¹)", "log")).toBeNull();
    });

    it("does not add one to a linear axis, where the linked range would misplace ticks", () => {
        expect(wavelengthAxis("Wavevector (µm⁻¹)", "linear")).toBeNull();
        expect(wavelengthAxis("Wavevector (µm⁻¹)", null)).toBeNull();
    });

    it("does not add one when the unit is not a reciprocal length", () => {
        expect(wavelengthAxis("Wavevector", "log")).toBeNull();
        expect(wavelengthAxis("Wavevector (µm)", "log")).toBeNull();
    });
});

describe("wavelengthRange", () => {
    it("inverts the interval", () => {
        const range = wavelengthRange(1, 10);
        expect(range.start).toBeCloseTo(2 * Math.PI);
        expect(range.end).toBeCloseTo(2 * Math.PI / 10);
    });

    it("returns a range that runs from large to small wavelengths", () => {
        const range = wavelengthRange(0.1, 100);
        expect(range.start).toBeGreaterThan(range.end);
    });

    it("has no result while the primary range is unknown or unusable", () => {
        expect(wavelengthRange(null, 10)).toBeNull();
        expect(wavelengthRange(1, null)).toBeNull();
        expect(wavelengthRange(0, 10)).toBeNull();
        expect(wavelengthRange(-1, 10)).toBeNull();
        expect(wavelengthRange(1, Infinity)).toBeNull();
        expect(wavelengthRange(NaN, 10)).toBeNull();
    });
});
