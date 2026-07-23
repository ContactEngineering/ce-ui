/**
 * Helpers for working with topography (measurement) API objects.
 */

/**
 * An empty topography object, used as a template for batch editing where only
 * the fields that were actually filled in are sent to the server.
 */
export function emptyTopography(): any {
    return {
        url: null,  // There is no representation of this topography on the server side
        name: null,
        channel_names: null,
        description: null,
        measurement_date: null,
        size_editable: true,
        size_x: null,
        size_y: null,
        unit_editable: true,
        unit: null,
        height_scale_editable: true,
        height_scale: null,
        fill_undefined_surface_mode: null,
        detrend_mode: null,
        is_periodic: null,
        instrument_name: null,
        instrument_type: null,
        instrument_parameters: null,
        thumbnail: null,
        tags: []
    };
}

/**
 * Reduce a topography object to the subset of non-null entries that may be
 * sent in a PATCH request, honoring the server-side editability flags.
 */
export function filterTopographyForPatchRequest(topography: any): any {
    const writeableEntries: string[] = [
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

    const patch: any = {};
    for (const e of writeableEntries) {
        if (topography[e] != null) {
            patch[e] = topography[e];
        }
    }
    return patch;
}
