/* The "sharing status" filter of the dataset list; values are the API's. */

export interface SharingStatusChoice {
    text: string;
    value: "all" | "own" | "others" | "published";
}

export const SHARING_STATUS_CHOICES: SharingStatusChoice[] = [
    {text: "All accessible datasets", value: "all"},
    {text: "Unpublished datasets created by me", value: "own"},
    {text: "Unpublished datasets created by others", value: "others"},
    {text: "Published datasets", value: "published"}
];

/* Visitors who are not signed in can only see published datasets, so that is
   the only choice that makes sense for them (ce-ui#308). */
export function sharingStatusChoicesFor(isAnonymous: boolean): SharingStatusChoice[] {
    return isAnonymous
        ? SHARING_STATUS_CHOICES.filter(choice => choice.value === "published")
        : SHARING_STATUS_CHOICES;
}

export function initialSharingStatus(isAnonymous: boolean): SharingStatusChoice["value"] {
    return isAnonymous ? "published" : "all";
}
