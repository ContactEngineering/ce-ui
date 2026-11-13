import {describe, expect, it} from "vitest";

import {needsUserDetails, rowForNewUser, rowFromUserPermission} from "@/utils/permissions";

const BOB = {url: "/users/v1/user/2/", name: "Bob Marley"};

describe("rowFromUserPermission", () => {
    it("keeps the embedded user so the row can show the name right away", () => {
        const row = rowFromUserPermission({user: BOB, allow: "edit", is_current_user: false});
        expect(row).toEqual({user: BOB.url, permission: "edit", isCurrentUser: false, userData: BOB});
    });

    it("still fetches the user for the ORCID iD, which is not embedded", () => {
        expect(needsUserDetails(rowFromUserPermission({user: BOB, allow: "view"}))).toBe(true);
    });
});

describe("rowForNewUser", () => {
    it("uses the search result instead of fetching the user (topobank#1425)", () => {
        const found = {...BOB, orcid: "0000-0002-1825-009X"};
        const row = rowForNewUser(found);
        expect(row).toEqual({user: BOB.url, permission: "view", userData: found});
        expect(needsUserDetails(row)).toBe(false);
    });

    it("treats a user without ORCID iD as fully known", () => {
        expect(needsUserDetails(rowForNewUser({...BOB, orcid: null}))).toBe(false);
    });
});

describe("needsUserDetails", () => {
    it("fetches when nothing is known about the user", () => {
        expect(needsUserDetails({user: BOB.url, permission: "view"})).toBe(true);
    });
});
