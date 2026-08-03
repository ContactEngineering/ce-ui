import {describe, expect, it} from "vitest";

import {describeVersions, publicationDate} from "@/utils/versions";

function publication(version: number, surfaceId: number, datetime: string | null = "2024-03-04T05:06:07Z") {
    return {
        version: version,
        datetime: datetime,
        surface: `http://testserver/manager/api/surface/${surfaceId}/`
    };
}

describe("describeVersions", () => {
    it("orders versions newest first", () => {
        const versions = describeVersions(
            [publication(1, 11), publication(3, 13), publication(2, 12)], 3);
        expect(versions.map(v => v.version)).toEqual([3, 2, 1]);
    });

    it("links each version to its dataset page", () => {
        const [version] = describeVersions([publication(2, 42)], 2);
        expect(version.href).toBe("/ui/dataset-detail/42/");
    });

    it("marks the version the row shows", () => {
        const versions = describeVersions([publication(1, 11), publication(2, 12)], 2);
        expect(versions.map(v => v.isCurrent)).toEqual([true, false]);
    });

    it("reports the publication date", () => {
        const [version] = describeVersions([publication(1, 11)], 1);
        expect(version.date).toBe("2024-03-04");
    });

    it("tolerates a publication without a date", () => {
        const [version] = describeVersions([publication(1, 11, null)], 1);
        expect(version.date).toBeNull();
    });

    it("skips a publication whose dataset is not readable", () => {
        const versions = describeVersions(
            [publication(1, 11), {version: 2, datetime: null, surface: null}], 1);
        expect(versions.map(v => v.version)).toEqual([1]);
    });

    it("has no entries before the versions have been fetched", () => {
        expect(describeVersions(null, 1)).toEqual([]);
        expect(describeVersions(undefined, 1)).toEqual([]);
        expect(describeVersions([], 1)).toEqual([]);
    });
});

describe("publicationDate", () => {
    it("keeps the date and drops the time", () => {
        expect(publicationDate("2024-03-04T05:06:07Z")).toBe("2024-03-04");
    });

    it("has no result for a missing or unparseable timestamp", () => {
        expect(publicationDate(null)).toBeNull();
        expect(publicationDate(undefined)).toBeNull();
        expect(publicationDate("whenever")).toBeNull();
    });
});
