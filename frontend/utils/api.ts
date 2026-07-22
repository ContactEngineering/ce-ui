/**
 * Helpers for talking to the topobank REST API.
 */

/** Serialize a subjects dictionary (e.g. {surface: [123]}) for use in a URL. */
export function subjectsToBase64(subjects: any): string {
    return btoa(JSON.stringify(subjects));
}

/** Inverse of `subjectsToBase64`. */
export function subjectsFromBase64(subjects: string): any {
    return JSON.parse(atob(subjects));
}

/** Extract the numeric object id from an API URL such as "/manager/api/surface/123/". */
export function getIdFromUrl(url: string): number {
    const s = url.split('/');
    return Number(s[s.length - 2]);
}
