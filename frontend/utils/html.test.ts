import {describe, expect, it} from "vitest";

import {escapeHtml} from "@/utils/html";

describe("escapeHtml", () => {
    it("escapes HTML special characters", () => {
        expect(escapeHtml(`<a href="x">it's &fun</a>`))
            .toBe("&lt;a href=&quot;x&quot;&gt;it&#39;s &amp;fun&lt;/a&gt;");
    });

    it("stringifies non-string input", () => {
        expect(escapeHtml(42)).toBe("42");
        expect(escapeHtml(null)).toBe("");
        expect(escapeHtml(undefined)).toBe("");
    });
});
