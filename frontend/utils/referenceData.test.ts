import {describe, expect, it} from "vitest";

import {buildReferenceDataSources} from "@/utils/referenceData";

const PSD_FUNCTION = "topobank_statistics.power_spectral_density";
const RMS_HEIGHT_FUNCTION = "topobank_statistics.variable_bandwidth";

describe("buildReferenceDataSources", () => {
    it("returns nothing for a workflow with no registered reference data", () => {
        expect(buildReferenceDataSources(["psd-rough-median"], "some_other_workflow", [], null, null))
            .toEqual([]);
    });

    it("silently skips a key that is not registered", () => {
        expect(buildReferenceDataSources(["not-a-real-key"], PSD_FUNCTION, [], null, null))
            .toEqual([]);
    });

    it("scales the curve to the card's current axis units", () => {
        const [source] = buildReferenceDataSources(
            ["psd-rough-median"], PSD_FUNCTION, [], "Wavevector (µm⁻¹)", "PSD (µm³)");
        expect(source.xScaleFactor).toBeCloseTo(1e-6);
        expect(source.yScaleFactor).toBeCloseTo(1e18);
        expect(source.url).toBe("/static/reference_data/psd/rougher_surface_median.json");
        expect(source.visible).toBe(true);
    });

    it("falls back to no rescaling for an axis unit it does not recognize", () => {
        const [source] = buildReferenceDataSources(
            ["psd-rough-median"], PSD_FUNCTION, [], "Something (V)", null);
        expect(source.xScaleFactor).toBe(1);
        expect(source.yScaleFactor).toBe(1);
    });

    it("gives two surfaces distinct subjects but shares one series chip for the same quartile", () => {
        const [rough, smooth] = buildReferenceDataSources(
            ["psd-rough-median", "psd-smooth-median"], PSD_FUNCTION, [], null, null);
        expect(rough.subjectNameIndex).not.toBe(smooth.subjectNameIndex);
        expect(rough.seriesNameIndex).toBe(smooth.seriesNameIndex);
    });

    it("gives the three quartiles of one surface the same subject but distinct series chips", () => {
        const [median, lower, upper] = buildReferenceDataSources(
            ["psd-rough-median", "psd-rough-lower-quartile", "psd-rough-upper-quartile"],
            PSD_FUNCTION, [], null, null);
        expect(median.subjectNameIndex).toBe(lower.subjectNameIndex);
        expect(median.subjectNameIndex).toBe(upper.subjectNameIndex);
        expect(new Set([median.seriesNameIndex, lower.seriesNameIndex, upper.seriesNameIndex]).size).toBe(3);
    });

    it("does not collide with category indices already used by real data sources", () => {
        const existing = [
            {subjectName: "Measurement A", subjectNameIndex: 0, seriesName: "Power spectral density", seriesNameIndex: 0},
            {subjectName: "Measurement B", subjectNameIndex: 1, seriesName: "Power spectral density", seriesNameIndex: 0},
        ];
        const [source] = buildReferenceDataSources(["psd-rough-median"], PSD_FUNCTION, existing, null, null);
        expect(source.subjectNameIndex).toBe(2);
        expect(source.seriesNameIndex).toBe(1);
    });

    it("uses grey for the rough surface and honey for the smooth one, regardless of workflow", () => {
        for (const [functionName, mediumKeys] of [
            [PSD_FUNCTION, ["psd-rough-median", "psd-smooth-median"]],
            [RMS_HEIGHT_FUNCTION, ["rms-rough-median", "rms-smooth-median"]],
        ] as const) {
            const [rough, smooth] = buildReferenceDataSources(mediumKeys, functionName, [], null, null);
            expect(rough.color).toBe("#808080");
            expect(smooth.color).toBe("#D9A521");
        }
    });

    it("uses a solid line for the median and a dashed one for either quartile bound", () => {
        const [median, lower, upper] = buildReferenceDataSources(
            ["psd-rough-median", "psd-rough-lower-quartile", "psd-rough-upper-quartile"],
            PSD_FUNCTION, [], null, null);
        expect(median.dash).toBe("solid");
        expect(lower.dash).toBe("dashed");
        expect(upper.dash).toBe("dashed");
    });

    it("never shows point markers on a reference curve", () => {
        const [source] = buildReferenceDataSources(["psd-rough-median"], PSD_FUNCTION, [], null, null);
        expect(source.showSymbols).toBe(false);
    });

    it("labels checkboxes as requested: 'STC consensus (rough/smooth surface) - median/lower IQR/upper IQR'", () => {
        const REFERENCE_DATASETS = Object.fromEntries(
            [PSD_FUNCTION].map(fn => [fn, buildReferenceDataSources(
                ["psd-rough-median", "psd-rough-lower-quartile", "psd-rough-upper-quartile",
                    "psd-smooth-median", "psd-smooth-lower-quartile", "psd-smooth-upper-quartile"],
                fn, [], null, null)]));
        const subjects = REFERENCE_DATASETS[PSD_FUNCTION].map((s: any) => s.subjectName);
        expect(subjects).toContain("STC consensus (rough surface)");
        expect(subjects).toContain("STC consensus (smooth surface)");
    });

    it("registers the RMS height (variable bandwidth) workflow with the same 6 datasets", () => {
        const sources = buildReferenceDataSources(
            ["rms-rough-median", "rms-rough-lower-quartile", "rms-rough-upper-quartile",
                "rms-smooth-median", "rms-smooth-lower-quartile", "rms-smooth-upper-quartile"],
            RMS_HEIGHT_FUNCTION, [], null, null);
        expect(sources).toHaveLength(6);
        expect(sources.map((s: any) => s.url)).toContain("/static/reference_data/rms_height/rougher_surface_median.json");
    });

    it("does not rescale RMS height (a plain length, exponent 1) when the axis is already in metres", () => {
        const [source] = buildReferenceDataSources(
            ["rms-rough-median"], RMS_HEIGHT_FUNCTION, [], "Bandwidth (nm)", "RMS height (nm)");
        expect(source.xScaleFactor).toBeCloseTo(1e9);
        expect(source.yScaleFactor).toBeCloseTo(1e9);
    });
});
