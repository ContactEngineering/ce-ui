import {describe, expect, it} from "vitest";

import {countTaskStates} from "@/utils/tasks";

describe("countTaskStates", () => {
    const analyses = [
        {task_state: "pe"},
        {task_state: "st"},
        {task_state: "su"},
        {task_state: "su"},
        {task_state: "fa"}
    ];

    it("counts analyses in the given states", () => {
        expect(countTaskStates(analyses, ["su"])).toBe(2);
        expect(countTaskStates(analyses, ["pe", "st"])).toBe(2);
        expect(countTaskStates(analyses, [])).toBe(0);
    });

    it("returns 0 for missing analyses", () => {
        expect(countTaskStates(null, ["su"])).toBe(0);
        expect(countTaskStates(undefined as any, ["su"])).toBe(0);
    });
});
