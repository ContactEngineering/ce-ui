import {describe, expect, it} from "vitest";

import {getIdFromUrl, subjectsFromBase64, subjectsToBase64} from "@/utils/api";

describe("subjectsToBase64 / subjectsFromBase64", () => {
    it("round-trips a subjects dictionary", () => {
        const subjects = {surface: [1, 2], topography: [3]};
        expect(subjectsFromBase64(subjectsToBase64(subjects))).toEqual(subjects);
    });

    it("encodes to URL-safe base64 of the JSON representation", () => {
        expect(subjectsToBase64({surface: [1889]})).toBe(btoa('{"surface":[1889]}'));
    });
});

describe("getIdFromUrl", () => {
    it("extracts the trailing id from an API URL", () => {
        expect(getIdFromUrl("/manager/api/surface/123/")).toBe(123);
        expect(getIdFromUrl("https://example.org/manager/api/topography/42/")).toBe(42);
    });
});
