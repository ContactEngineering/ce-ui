import {describe, expect, it} from "vitest";

import {
    initialSharingStatus,
    SHARING_STATUS_CHOICES,
    sharingStatusChoicesFor
} from "@/utils/sharingStatus";

describe("sharing status filter", () => {
    it("offers signed-in users every choice, starting with all datasets", () => {
        expect(sharingStatusChoicesFor(false)).toEqual(SHARING_STATUS_CHOICES);
        expect(initialSharingStatus(false)).toBe("all");
    });

    it("offers anonymous visitors only published datasets (ce-ui#308)", () => {
        expect(sharingStatusChoicesFor(true).map(c => c.value)).toEqual(["published"]);
        expect(initialSharingStatus(true)).toBe("published");
    });

    it("starts on a value that is among the offered choices", () => {
        for (const isAnonymous of [false, true]) {
            const values = sharingStatusChoicesFor(isAnonymous).map(c => c.value);
            expect(values).toContain(initialSharingStatus(isAnonymous));
        }
    });
});
