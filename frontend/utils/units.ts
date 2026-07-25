/**
 * Helpers for picking a human-readable length unit for plot axes.
 *
 * Data is stored in whatever unit the measurement was recorded in, which is
 * often a poor fit for display: a scan recorded in metres but a few micrometres
 * long yields tick labels like `2.5e-6`. Rescaling the data to a unit that
 * matches its magnitude avoids the exponent entirely.
 */

/**
 * Decimal exponent (relative to metres) of each length unit we accept as input.
 * Mirrors `length_units` in `SurfaceTopography.Support.UnitConversion` and the
 * `LENGTH_UNIT_CHOICES` of the `Topography` model, including the non-SI-prefix
 * ångström and the ASCII spelling `um` of `µm`.
 */
export const LENGTH_UNIT_EXPONENTS: { [unit: string]: number } = {
    'Gm': 9,
    'Mm': 6,
    'km': 3,
    'm': 0,
    'mm': -3,
    'µm': -6,
    'um': -6,
    'nm': -9,
    'Å': -10,
    'pm': -12,
    'fm': -15,
};

/**
 * Units we are willing to display, keyed by decimal exponent. Only the
 * thousand-steps of the SI ladder appear here; ångström is accepted as input
 * but never chosen for display, as it would put ticks in a decade that reads
 * oddly next to its neighbours.
 */
const DISPLAY_UNITS: { [exponent: number]: string } = {
    9: 'Gm',
    6: 'Mm',
    3: 'km',
    0: 'm',
    [-3]: 'mm',
    [-6]: 'µm',
    [-9]: 'nm',
    [-12]: 'pm',
    [-15]: 'fm',
};

const MAX_EXPONENT = 9;
const MIN_EXPONENT = -15;

export interface UnitRescaling {
    /** The unit to display on the axis. */
    unit: string;
    /** Multiply data given in the original unit by this to obtain `unit`. */
    factor: number;
}

/** Rescaling that leaves the data untouched. */
function identity(unit: string): UnitRescaling {
    return {unit, factor: 1};
}

/**
 * Pick a length unit in which `magnitude` reads without an exponent.
 *
 * The returned unit is chosen so that `magnitude * factor` falls in [1, 1000),
 * e.g. a magnitude of 2.5e-6 m becomes 2.5 µm. Input units outside the known
 * set (including `null`, and non-length units such as a bare count) are passed
 * through unscaled, as are zero and non-finite magnitudes, which carry no
 * information about a sensible scale.
 *
 * @param magnitude A representative size of the data, e.g. the largest
 *     absolute value on the axis. Use the largest absolute value rather than
 *     the span, because it is the tick labels themselves — not their
 *     difference — that we are keeping short.
 * @param fromUnit The unit the data is currently expressed in.
 * @returns The display unit and the factor converting into it.
 */
export function rescaleLengthUnit(magnitude: number, fromUnit: string | null | undefined): UnitRescaling {
    if (fromUnit == null || !(fromUnit in LENGTH_UNIT_EXPONENTS)) {
        return identity(fromUnit as string);
    }
    if (typeof magnitude !== "number" || !isFinite(magnitude) || magnitude === 0) {
        return identity(fromUnit);
    }

    const fromExponent = LENGTH_UNIT_EXPONENTS[fromUnit];
    const magnitudeInMetres = Math.abs(magnitude) * Math.pow(10, fromExponent);

    // Round down to the nearest thousand-step so the scaled value lands in
    // [1, 1000), then clamp to the units we actually have names for.
    let exponent = 3 * Math.floor(Math.log10(magnitudeInMetres) / 3);
    exponent = Math.min(MAX_EXPONENT, Math.max(MIN_EXPONENT, exponent));

    // Both exponents are integers, so the factor is an exact power of ten
    // rather than the result of dividing two rounded decimals.
    return {unit: DISPLAY_UNITS[exponent], factor: Math.pow(10, fromExponent - exponent)};
}

/**
 * Largest absolute value in `values`, ignoring non-finite entries (undefined
 * data points in a measurement are stored as NaN).
 *
 * @param values The data to scan.
 * @returns The largest absolute value, or 0 if there is no finite entry.
 */
export function maxAbsolute(values: ArrayLike<number>): number {
    let max = 0;
    for (let i = 0; i < values.length; i++) {
        const v = Math.abs(values[i]);
        if (isFinite(v) && v > max) {
            max = v;
        }
    }
    return max;
}
