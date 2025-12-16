export function subjectsToBase64(subjects: any): string {
    return btoa(JSON.stringify(subjects));
}

export function subjectsFromBase64(subjects: string): any {
    return JSON.parse(atob(subjects));
}

export function getIdFromUrl(url: string): number {
    const s = url.split('/');
    return Number(s[s.length - 2]);
}

export function getNameFromUrl(url: string): string {
    const s = url.split('/');
    return s[s.length - 2];
}


export function filterTopographyForPatchRequest(topography: any): any {
    // Copy writable entries
    let writeableEntries: string[] = [
        'description', 'instrument_name', 'instrument_parameters', 'instrument_type', 'measurement_date', 'name',
        'tags', 'detrend_mode', 'fill_undefined_data_mode', 'data_source'
    ];
    if (topography.size_editable) {
        writeableEntries.push('size_x', 'size_y');
    }
    if (topography.unit_editable) {
        writeableEntries.push('unit');
    }
    if (topography.height_scale_editable) {
        writeableEntries.push('height_scale');
    }
    if (topography.is_periodic_editable) {
        writeableEntries.push('is_periodic');
    }

    let returnDict: {} = {};
    for (const e of writeableEntries) {
        if (topography[e] != null) {
            returnDict[e] = topography[e];
        }
    }

    // Uncomment to simulate error on PATCH
    // returnDict['thumbnail'] = 'def';

    return returnDict;
}
