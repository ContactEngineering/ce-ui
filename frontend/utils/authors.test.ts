import {describe, expect, it} from "vitest";

import {
    emptyAffiliation,
    emptyAuthor,
    formatAuthorList,
    isValidOrcidId,
    isValidRorId,
    validateAuthors
} from "@/utils/authors";

function author(firstName: string, lastName: string, orcidId: string = "") {
    const a = emptyAuthor();
    a.person.firstName = firstName;
    a.person.lastName = lastName;
    a.person.orcidId = orcidId;
    return a;
}

describe("isValidOrcidId", () => {
    it("accepts well-formed ORCID iDs", () => {
        expect(isValidOrcidId("0000-0002-1825-0097")).toBe(true);
        expect(isValidOrcidId("0000-0002-1825-009X")).toBe(true);
    });

    it("rejects malformed ORCID iDs", () => {
        expect(isValidOrcidId("0000-0002-1825-09")).toBe(false);
        expect(isValidOrcidId("0000000218250097")).toBe(false);
        expect(isValidOrcidId("")).toBe(false);
    });
});

describe("isValidRorId", () => {
    it("accepts well-formed ROR iDs", () => {
        expect(isValidRorId("05x2bcf33")).toBe(true);
    });

    it("rejects malformed ROR iDs", () => {
        expect(isValidRorId("15x2bcf33")).toBe(false);  // must start with 0
        expect(isValidRorId("05x2bcf3")).toBe(false);  // too short
        expect(isValidRorId("")).toBe(false);
    });
});

describe("validateAuthors", () => {
    it("accepts a complete author without ORCID iD", () => {
        const authors = [author("Ada", "Lovelace")];
        expect(validateAuthors(authors)).toBe(true);
        expect(authors[0].person.firstNameValid).toBe(true);
        expect(authors[0].person.lastNameValid).toBe(true);
        expect(authors[0].person.orcidIdValid).toBe(true);
    });

    it("rejects missing names and flags the offending fields", () => {
        const authors = [author("", "Lovelace")];
        expect(validateAuthors(authors)).toBe(false);
        expect(authors[0].person.firstNameValid).toBe(false);
        expect(authors[0].person.lastNameValid).toBe(true);
    });

    it("rejects malformed ORCID iDs", () => {
        expect(validateAuthors([author("Ada", "Lovelace", "not-an-orcid")])).toBe(false);
        expect(validateAuthors([author("Ada", "Lovelace", "0000-0002-1825-0097")])).toBe(true);
    });

    it("validates affiliations", () => {
        const a = author("Ada", "Lovelace");
        a.affiliations.push(emptyAffiliation());
        expect(validateAuthors([a])).toBe(false);  // affiliation name missing
        a.affiliations[0].name = "University of London";
        expect(validateAuthors([a])).toBe(true);
        a.affiliations[0].rorId = "invalid";
        expect(validateAuthors([a])).toBe(false);
    });
});

describe("formatAuthorList", () => {
    it("joins authors with commas", () => {
        expect(formatAuthorList([author("Ada", "Lovelace"), author("Charles", "Babbage")]))
            .toBe("Ada Lovelace, Charles Babbage");
    });
});
