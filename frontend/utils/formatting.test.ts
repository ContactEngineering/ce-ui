import {describe, expect, it} from "vitest";

import {
    formatDateTime,
    formatExponential,
    preferExponentialLabels,
    prettyBytes,
    unicodeSuperscript
} from "@/utils/formatting";

describe("unicodeSuperscript", () => {
    it("converts digits and signs to superscript", () => {
        expect(unicodeSuperscript("3")).toBe("³");
        expect(unicodeSuperscript("-12")).toBe("⁻¹²");
        expect(unicodeSuperscript("+2.5")).toBe("⁺²⋅⁵");
    });

    it("leaves other characters untouched", () => {
        expect(unicodeSuperscript("µm3")).toBe("µm³");
        expect(unicodeSuperscript("abc")).toBe("abc");
    });
});

describe("formatExponential", () => {
    it("passes through zero and non-finite values", () => {
        expect(formatExponential(0)).toBe("0");
        expect(formatExponential(NaN)).toBe("NaN");
        expect(formatExponential(Infinity)).toBe("Infinity");
        expect(formatExponential(-Infinity)).toBe("-Infinity");
        expect(formatExponential(undefined as any)).toBe("undefined");
    });

    it("does not attach an exponent for numbers of order one", () => {
        expect(formatExponential(1)).toBe("1");
        expect(formatExponential(2.5)).toBe("2.5");
        expect(formatExponential(-3.25)).toBe("-3.25");
    });

    it("formats powers of ten without a mantissa", () => {
        expect(formatExponential(1000)).toBe("10³");
        expect(formatExponential(0.01)).toBe("10⁻²");
        expect(formatExponential(-1000)).toBe("-10³");
    });

    it("formats generic numbers with mantissa and exponent", () => {
        expect(formatExponential(1300)).toBe("1.3×10³");
        expect(formatExponential(-1300)).toBe("-1.3×10³");
        expect(formatExponential(0.00025)).toBe("2.5×10⁻⁴");
    });

    it("respects the number of decimal places", () => {
        expect(formatExponential(1234.5, 1)).toBe("1.2×10³");
        expect(formatExponential(1234.5, 3)).toBe("1.235×10³");
    });

    it("rolls over to the next exponent when rounding up", () => {
        expect(formatExponential(999999, 2)).toBe("10⁶");
    });
});

describe("preferExponentialLabels", () => {
    // The label strings below are what Bokeh's BasicTickFormatter actually
    // produces for these ticks, including its unicode minus sign.
    it("keeps plain decimal labels untouched", () => {
        expect(preferExponentialLabels([0, 25, 50, 75, 100], ["0", "25", "50", "75", "100"]))
            .toEqual(["0", "25", "50", "75", "100"]);
        expect(preferExponentialLabels([-50, 0, 50], ["−50", "0", "50"]))
            .toEqual(["−50", "0", "50"]);
        expect(preferExponentialLabels([0.25, 0.5], ["0.25", "0.5"]))
            .toEqual(["0.25", "0.5"]);
    });

    it("replaces e-notation with powers of ten", () => {
        expect(preferExponentialLabels([1e-6, 2e-6, 3e-6], ["1.000e−6", "2.000e−6", "3.000e−6"]))
            .toEqual(["10⁻⁶", "2×10⁻⁶", "3×10⁻⁶"]);
        expect(preferExponentialLabels([1e6, 2e6], ["1.000e+6", "2.000e+6"]))
            .toEqual(["10⁶", "2×10⁶"]);
    });

    it("converts the whole set so one axis never mixes notations", () => {
        // Bokeh applies one precision to the whole set, so a plain-looking
        // label can sit beside an exponential one; both must be converted.
        expect(preferExponentialLabels([1, 1e6], ["1", "1.000e+6"]))
            .toEqual(["1", "10⁶"]);
    });

    it("recognises an upper-case exponent", () => {
        expect(preferExponentialLabels([1e6], ["1E+6"])).toEqual(["10⁶"]);
    });

    it("handles an empty tick set", () => {
        expect(preferExponentialLabels([], [])).toEqual([]);
    });
});

describe("prettyBytes", () => {
    it("formats byte counts human-readably", () => {
        expect(prettyBytes(0)).toBe("0 B");
        expect(prettyBytes(1)).toBe("1 B");
        expect(prettyBytes(1024)).toBe("1 kB");
        expect(prettyBytes(1536)).toBe("1.5 kB");
        expect(prettyBytes(1048576)).toBe("1 MB");
        expect(prettyBytes(1234567890)).toBe("1.15 GB");
    });

    it("caps at terabytes", () => {
        expect(prettyBytes(1024 ** 5)).toBe("1024 TB");
    });

    it("passes through invalid values", () => {
        expect(prettyBytes(NaN)).toBe("NaN");
        expect(prettyBytes(undefined as any)).toBe("undefined");
    });
});

describe("formatDateTime", () => {
    it("formats a parseable date", () => {
        const expected = new Date("2024-01-02T03:04:05Z").toLocaleString();
        expect(formatDateTime("2024-01-02T03:04:05Z")).toBe(expected);
    });

    it("returns null for missing or invalid input", () => {
        expect(formatDateTime(null)).toBeNull();
        expect(formatDateTime(undefined)).toBeNull();
        expect(formatDateTime("not a date")).toBeNull();
    });
});
