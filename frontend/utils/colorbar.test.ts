import {describe, expect, it} from "vitest";

import {computeColorbarTicks} from "@/utils/colorbar";

describe("computeColorbarTicks", () => {
    it("produces at most maxTicks ticks", () => {
        expect(computeColorbarTicks(0, 1).length).toBeLessThanOrEqual(15);
        expect(computeColorbarTicks(0, 1, 5).length).toBeLessThanOrEqual(5);
        expect(computeColorbarTicks(-123.4, 567.8).length).toBeLessThanOrEqual(15);
    });

    it("places ticks strictly inside the bar, ordered by increasing value", () => {
        const ticks = computeColorbarTicks(0, 1);
        expect(ticks.length).toBeGreaterThan(0);
        for (const tick of ticks) {
            expect(tick.relpos).toBeGreaterThan(0);
            expect(tick.relpos).toBeLessThan(100);
        }
        // Increasing values sit closer to the top of the bar, i.e. relpos decreases
        const positions = ticks.map(t => t.relpos);
        expect(positions).toEqual([...positions].sort((a, b) => b - a));
    });

    it("uses round tick values", () => {
        const ticks = computeColorbarTicks(0, 1);
        // Range 1 => tick distance 0.1 => labels with one fraction digit
        expect(ticks.map(t => t.label)).toEqual(
            ["0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9"]);
    });

    it("labels integer ranges without fraction digits", () => {
        const ticks = computeColorbarTicks(0, 100);
        expect(ticks[0].label).toBe("10");
        expect(ticks[ticks.length - 1].label).toBe("90");
    });

    it("handles ranges not starting at zero", () => {
        const ticks = computeColorbarTicks(-0.5, 0.5);
        expect(ticks.some(t => t.label === "0.0")).toBe(true);
    });
});
