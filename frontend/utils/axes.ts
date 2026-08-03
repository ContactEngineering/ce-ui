/**
 * Helpers for the secondary real-space axis on reciprocal-space plots.
 *
 * A power-spectral density is plotted against wavevector, which is the quantity
 * the mathematics is written in but not the one a reader thinks in. Showing the
 * corresponding wavelength λ = 2π/q on a second axis above the plot makes the
 * size scale a feature appears at readable directly off the figure.
 */

import {LENGTH_UNIT_EXPONENTS} from "@/utils/units";

/** The quantity whose axis gets a wavelength counterpart, lower-cased. */
const WAVEVECTOR = "wavevector";

/**
 * A reciprocal length, in the spellings the backend produces (`µm⁻¹`, built
 * from the measurement's unit) and the ones a hand-written label might use
 * (`1/µm`, `µm^-1`).
 */
const RECIPROCAL_UNIT_PATTERNS = [
    /^1\s*\/\s*(\S+)$/,
    /^(\S+?)\s*⁻¹$/,
    /^(\S+?)\s*\^-1$/,
];

export interface AxisLabel {
    /** The quantity, e.g. "Wavevector". */
    quantity: string;
    /** The unit from the trailing parenthesis, or null if the label has none. */
    unit: string | null;
}

/**
 * Split an axis label into the quantity and its unit.
 *
 * The backend appends the unit in parentheses (`"Wavevector (µm⁻¹)"`), which is
 * the only place the unit of an axis is available to us — the card
 * configuration does not carry it separately.
 *
 * @param label The axis label.
 * @returns The quantity and unit.
 */
export function parseAxisLabel(label: string | null | undefined): AxisLabel {
    if (label == null) {
        return {quantity: "", unit: null};
    }
    const match = /^(.*?)\s*\(([^()]*)\)\s*$/.exec(label);
    if (match == null) {
        return {quantity: label.trim(), unit: null};
    }
    return {quantity: match[1].trim(), unit: match[2].trim()};
}

/**
 * The length unit a reciprocal-length unit is built from.
 *
 * @param unit The unit to inspect, e.g. "µm⁻¹".
 * @returns The length unit ("µm"), or null if this is not a reciprocal length.
 *     A reciprocal of something that is not a length — the curvature
 *     distribution is also plotted against `µm⁻¹` — has no length unit and is
 *     rejected here, but note that it is the quantity, not the unit, that makes
 *     a wavelength axis meaningful; see `wavelengthAxis`.
 */
export function reciprocalLengthUnit(unit: string | null | undefined): string | null {
    if (unit == null) {
        return null;
    }
    for (const pattern of RECIPROCAL_UNIT_PATTERNS) {
        const match = pattern.exec(unit.trim());
        if (match != null && match[1] in LENGTH_UNIT_EXPONENTS) {
            return match[1];
        }
    }
    return null;
}

export interface WavelengthAxis {
    /** Label for the secondary axis, including its unit. */
    label: string;
    /** Length unit of the secondary axis. */
    unit: string;
}

/**
 * Decide whether a plot gets a wavelength axis, and how it is labelled.
 *
 * Two conditions, both necessary:
 *
 * 1. The x axis carries a wavevector. A reciprocal length alone is not enough —
 *    the curvature distribution is plotted against `µm⁻¹` as well, and 2π over
 *    a curvature is not a size scale.
 * 2. The x axis is logarithmic. The secondary axis is a Bokeh range linked to
 *    the primary one, and such a link can only express a mapping that is affine
 *    in the coordinates the axis is drawn in. `log λ = log 2π − log q` is affine
 *    in log space, so a log axis is exact; on a linear axis the same link would
 *    silently misplace every tick.
 *
 * @param label The label of the primary x axis.
 * @param axisType The Bokeh axis type of the primary x axis.
 * @returns The secondary axis to add, or null if this plot gets none.
 */
export function wavelengthAxis(label: string | null | undefined,
                               axisType: string | null | undefined): WavelengthAxis | null {
    if (axisType !== "log") {
        return null;
    }
    const {quantity, unit} = parseAxisLabel(label);
    if (quantity.toLowerCase() !== WAVEVECTOR) {
        return null;
    }
    const lengthUnit = reciprocalLengthUnit(unit);
    if (lengthUnit == null) {
        return null;
    }
    // Naming the relation spells out for a reader who has not met a PSD before
    // how the two axes belong together.
    return {label: `Wavelength λ = 2π/q (${lengthUnit})`, unit: lengthUnit};
}

/**
 * The wavelength interval corresponding to a wavevector interval.
 *
 * λ = 2π/q inverts the order of the interval, so the returned range runs from
 * large to small wavelengths, matching the left-to-right direction of the
 * wavevector axis below it.
 *
 * @param start Lower end of the wavevector range.
 * @param end Upper end of the wavevector range.
 * @returns Start and end of the wavelength range, or null while the primary
 *     range is not yet known or does not admit a wavelength (a wavevector of
 *     zero has no finite wavelength).
 */
export function wavelengthRange(start: number | null | undefined,
                                end: number | null | undefined): { start: number, end: number } | null {
    if (typeof start !== "number" || typeof end !== "number") {
        return null;
    }
    if (!isFinite(start) || !isFinite(end) || start <= 0 || end <= 0) {
        return null;
    }
    return {start: 2 * Math.PI / start, end: 2 * Math.PI / end};
}
