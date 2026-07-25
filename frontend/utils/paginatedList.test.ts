import {describe, expect, it} from "vitest";

import {formatBytes, formatDuration, formatTimestamp} from "@/utils/paginatedList";

describe("formatDuration", () => {
    it("shows sub-minute durations in seconds", () => {
        expect(formatDuration(0.5)).toBe("0.5 s");
        expect(formatDuration(59.9)).toBe("59.9 s");
    });

    it("shows minutes and seconds below an hour", () => {
        expect(formatDuration(60)).toBe("1 min 00 s");
        expect(formatDuration(192)).toBe("3 min 12 s");
    });

    it("shows hours and minutes above an hour", () => {
        expect(formatDuration(3600)).toBe("1 h 00 min");
        expect(formatDuration(3840)).toBe("1 h 04 min");
    });

    it("renders a dash for a task that has not started", () => {
        expect(formatDuration(null)).toBe("–");
    });
});

describe("formatBytes", () => {
    it("scales to a readable unit", () => {
        expect(formatBytes(512)).toBe("512 B");
        expect(formatBytes(2048)).toBe("2.0 kB");
        expect(formatBytes(5 * 1024 * 1024)).toBe("5.0 MB");
    });

    it("renders a dash when memory was not recorded", () => {
        expect(formatBytes(null)).toBe("–");
    });
});

describe("formatTimestamp", () => {
    it("renders a dash for a missing timestamp", () => {
        expect(formatTimestamp(null)).toBe("–");
    });

    it("renders a locale string for a real timestamp", () => {
        const formatted = formatTimestamp("2026-07-25T10:30:00Z");
        expect(formatted).not.toBe("–");
        expect(formatted).toContain("2026");
    });
});
