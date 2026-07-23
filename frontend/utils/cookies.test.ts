import {describe, expect, it} from "vitest";

import {getCookieFromString} from "@/utils/cookies";

describe("getCookieFromString", () => {
    it("extracts a named cookie", () => {
        expect(getCookieFromString("csrftoken=abc123; theme=dark", "csrftoken")).toBe("abc123");
        expect(getCookieFromString("csrftoken=abc123; theme=dark", "theme")).toBe("dark");
    });

    it("returns null for missing cookies", () => {
        expect(getCookieFromString("", "csrftoken")).toBeNull();
        expect(getCookieFromString("theme=dark", "csrftoken")).toBeNull();
    });

    it("does not confuse cookies whose names share a prefix", () => {
        expect(getCookieFromString("xcsrftoken=nope", "csrftoken")).toBeNull();
    });

    it("decodes URI-encoded values and preserves '=' inside values", () => {
        expect(getCookieFromString("next=%2Fui%2Fdataset-list%2F", "next")).toBe("/ui/dataset-list/");
        expect(getCookieFromString("token=a=b=c", "token")).toBe("a=b=c");
    });
});
