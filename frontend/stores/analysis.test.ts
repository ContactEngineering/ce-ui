import {beforeEach, describe, expect, it} from "vitest";
import {createPinia, setActivePinia} from "pinia";

import {useAnalysisStore} from "@/stores/analysis";

const PSD = "topobank_statistics.power_spectral_density";
const ACF = "topobank_statistics.autocorrelation";

describe("useAnalysisStore", () => {
    beforeEach(() => {
        setActivePinia(createPinia());
    });

    it("starts with no workflow selected", () => {
        const analysis = useAnalysisStore();

        expect(analysis.workflows).toEqual([]);
        expect(analysis.isSelected(PSD)).toBe(false);
    });

    it("remembers which workflows are to be shown", () => {
        const analysis = useAnalysisStore();

        analysis.select(PSD);
        analysis.select(ACF);

        expect(analysis.workflows).toEqual([PSD, ACF]);
        expect(analysis.isSelected(PSD)).toBe(true);
        expect(analysis.isSelected(ACF)).toBe(true);
    });

    it("removes only the workflow that was unselected", () => {
        const analysis = useAnalysisStore();
        analysis.select(PSD);
        analysis.select(ACF);

        analysis.unselect(PSD);

        expect(analysis.workflows).toEqual([ACF]);
        expect(analysis.isSelected(PSD)).toBe(false);
        expect(analysis.isSelected(ACF)).toBe(true);
    });

    it("ignores unselecting a workflow that was never selected", () => {
        const analysis = useAnalysisStore();
        analysis.select(PSD);

        analysis.unselect(ACF);

        expect(analysis.workflows).toEqual([PSD]);
    });

    it("drops every workflow on clear", () => {
        const analysis = useAnalysisStore();
        analysis.select(PSD);
        analysis.select(ACF);

        analysis.clear();

        expect(analysis.workflows).toEqual([]);
        expect(analysis.isSelected(ACF)).toBe(false);
    });

    it("does not confuse workflows whose names share a prefix", () => {
        const analysis = useAnalysisStore();

        analysis.select("topobank_statistics.height_distribution");

        // `includes` matches whole entries, not substrings
        expect(analysis.isSelected("topobank_statistics.height")).toBe(false);
        expect(analysis.isSelected("topobank_statistics.height_distribution")).toBe(true);
    });
});
