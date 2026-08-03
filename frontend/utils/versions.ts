/**
 * Helpers for the published versions of a dataset.
 *
 * The dataset list shows only the latest version of a dataset, so a row has to
 * offer the older ones: publishing creates a separate dataset, and without a way
 * in from the list they are only reachable by knowing they exist.
 */

import {getIdFromUrl} from "@/utils/api";

export interface DatasetVersion {
    /** Version number, as published. */
    version: number;
    /** Publication date, `YYYY-MM-DD`, or null if the publication carries none. */
    date: string | null;
    /** Link to the dataset page of this version. */
    href: string;
    /** Whether this is the version the row itself shows. */
    isCurrent: boolean;
}

/**
 * Turn the publications of a dataset into the entries of the version list,
 * newest first.
 *
 * @param publications Publications as returned by the publication API, i.e.
 *     carrying `version`, `datetime` and a `surface` URL.
 * @param currentVersion The version the row shows, marked in the result.
 * @returns One entry per publication, ordered from newest to oldest.
 */
export function describeVersions(publications: any[] | null | undefined,
                                 currentVersion: number | null | undefined): DatasetVersion[] {
    if (publications == null) {
        return [];
    }
    return publications
        .filter(publication => publication?.surface != null)
        .map(publication => ({
            version: publication.version,
            date: publicationDate(publication.datetime),
            href: `/ui/dataset-detail/${getIdFromUrl(publication.surface)}/`,
            isCurrent: publication.version === currentVersion
        }))
        .sort((a, b) => b.version - a.version);
}

/**
 * The date part of a publication timestamp.
 *
 * @param datetime An ISO timestamp, as the API reports it.
 * @returns The date as `YYYY-MM-DD`, or null if there is none to show.
 */
export function publicationDate(datetime: string | null | undefined): string | null {
    if (datetime == null) {
        return null;
    }
    const date = new Date(datetime);
    return isNaN(date.getTime()) ? null : date.toISOString().substring(0, 10);
}
