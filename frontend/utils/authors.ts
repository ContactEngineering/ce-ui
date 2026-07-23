/**
 * Author metadata handling for the publication wizard.
 */

export interface Person {
    firstName: string;
    firstNameValid: boolean | null;
    lastName: string;
    lastNameValid: boolean | null;
    orcidId: string;
    orcidIdValid: boolean | null;
}

export interface Affiliation {
    name: string;
    nameValid: boolean | null;
    rorId: string;
    rorIdValid: boolean | null;
}

export interface Author {
    person: Person;
    affiliations: Affiliation[];
}

const orcidIdRegex = /^(\d{4}-){3}\d{3}(\d|X)$/;
const rorIdRegex = /^0[a-z|0-9]{6}[0-9]{2}$/;

export function isValidOrcidId(orcidId: string): boolean {
    return orcidIdRegex.test(orcidId);
}

export function isValidRorId(rorId: string): boolean {
    return rorIdRegex.test(rorId);
}

export function emptyPerson(): Person {
    return {
        firstName: "",
        firstNameValid: null,
        lastName: "",
        lastNameValid: null,
        orcidId: "",
        orcidIdValid: null
    };
}

export function emptyAuthor(): Author {
    return {
        person: emptyPerson(),
        affiliations: []
    };
}

export function emptyAffiliation(): Affiliation {
    return {
        name: "",
        nameValid: null,
        rorId: "",
        rorIdValid: null
    };
}

/**
 * Validate an author list in place: the `*Valid` flags of each author and
 * affiliation are updated (they drive the highlighting of the input fields).
 *
 * @returns true if all authors and affiliations are valid.
 */
export function validateAuthors(authors: Author[]): boolean {
    for (const author of authors) {
        author.person.firstNameValid = author.person.firstName !== "";
        author.person.lastNameValid = author.person.lastName !== "";
        author.person.orcidIdValid =
            author.person.orcidId === "" || isValidOrcidId(author.person.orcidId);
        for (const affiliation of author.affiliations) {
            affiliation.nameValid = affiliation.name !== "";
            affiliation.rorIdValid =
                affiliation.rorId === "" || isValidRorId(affiliation.rorId);
        }
    }
    return authors.every(x =>
        x.person.firstNameValid &&
        x.person.lastNameValid &&
        x.person.orcidIdValid &&
        x.affiliations.every(y => y.nameValid && y.rorIdValid));
}

/** Format an author list the way it will appear in the citation. */
export function formatAuthorList(authors: Author[]): string {
    return authors
        .map(author => `${author.person.firstName} ${author.person.lastName}`)
        .join(", ");
}
