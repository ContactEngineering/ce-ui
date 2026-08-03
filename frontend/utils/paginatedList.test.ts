import {describe, expect, it} from "vitest";

import {formatBytes, formatTimestamp} from "@/utils/paginatedList";

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
