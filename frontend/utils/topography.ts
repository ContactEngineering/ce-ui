import {formatExponential, formatSignificant} from "@/utils/formatting";

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

/**
 * Describe the trend that detrending subtracted from a measurement.
 *
 * The backend fits the trend while reading the file and reports only the
 * components its detrend mode determines: a measurement that merely has its mean
 * subtracted has none, a line scan has no y component, and a direction the fit
 * found to be flat has no radius.
 *
 * @param parameters The `detrend_parameters` of the measurement, as reported by
 *     the API. Null for a measurement that has not been inspected.
 * @param unit The lateral unit of the measurement, in which radii are given.
 * @returns A description such as "slope 2.5×10⁻³ in x, radius 50 µm in x", or
 *     null when no trend was fitted.
 */
export function describeDetrend(parameters: any, unit: string | null | undefined): string | null {
    if (parameters == null) {
        return null;
    }
    const parts: string[] = [];
    for (const direction of ["x", "y"]) {
        const slope = parameters[`slope_${direction}`];
        if (slope != null) {
            parts.push(`slope ${formatQuantity(slope)} in ${direction}`);
        }
    }
    for (const direction of ["x", "y"]) {
        const radius = parameters[`radius_${direction}`];
        if (radius != null) {
            const withUnit = unit == null ? formatQuantity(radius) : `${formatQuantity(radius)} ${unit}`;
            parts.push(`radius ${withUnit} in ${direction}`);
        }
    }
    return parts.length === 0 ? null : parts.join(", ");
}

/* Plain decimals stay readable down to about a thousandth; below that they turn
   into a row of zeros, which is where the site's exponential notation takes over. */
function formatQuantity(value: number): string {
    return Math.abs(value) >= 1e-3 ? formatSignificant(value, 3) : formatExponential(value, 2);
}
