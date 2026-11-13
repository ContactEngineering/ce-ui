import {describe, expect, it} from "vitest";

import {renewErrorMessage} from "@/utils/renew";

describe("renewErrorMessage", () => {
    it("asks to sign in when renewing is not allowed (topobank#1406)", () => {
        for (const status of [401, 403]) {
            expect(renewErrorMessage({response: {status}, message: "Request failed"}))
                .toMatch(/sign in/i);
        }
    });

    it("passes on other errors", () => {
        expect(renewErrorMessage({response: {status: 500}, message: "Request failed with status code 500"}))
            .toBe("Request failed with status code 500");
        expect(renewErrorMessage({message: "Network Error"})).toBe("Network Error");
        expect(renewErrorMessage("boom")).toBe("boom");
    });
});
