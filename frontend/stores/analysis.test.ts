import {beforeEach, describe, expect, it} from "vitest";
import {createPinia, setActivePinia} from "pinia";

import {useAnalysisStore} from "@/stores/analysis";

describe("useAnalysisStore", () => {
    beforeEach(() => {
        setActivePinia(createPinia());
    });

    it("selects and unselects individual workflows", () => {
        const analysis = useAnalysisStore();
        analysis.select("power-spectrum");
        expect(analysis.isSelected("power-spectrum")).toBe(true);
        expect(analysis.isSelected("contact-mechanics")).toBe(false);
        analysis.unselect("power-spectrum");
        expect(analysis.isSelected("power-spectrum")).toBe(false);
    });

    it("selects all workflows at once", () => {
        const analysis = useAnalysisStore();
        analysis.selectAll(["power-spectrum", "contact-mechanics"]);
        expect(analysis.workflows).toEqual(["power-spectrum", "contact-mechanics"]);
    });

    it("does not duplicate workflows that were already selected", () => {
        const analysis = useAnalysisStore();
        analysis.select("power-spectrum");
        analysis.selectAll(["power-spectrum", "contact-mechanics"]);
        expect(analysis.workflows).toEqual(["power-spectrum", "contact-mechanics"]);
    });

    it("keeps no reference to the list it was given", () => {
        const analysis = useAnalysisStore();
        const workflows = ["power-spectrum"];
        analysis.selectAll(workflows);
        workflows.push("contact-mechanics");
        expect(analysis.workflows).toEqual(["power-spectrum"]);
    });

    it("clears the selection", () => {
        const analysis = useAnalysisStore();
        analysis.selectAll(["power-spectrum", "contact-mechanics"]);
        analysis.clear();
        expect(analysis.workflows).toEqual([]);
    });
});
