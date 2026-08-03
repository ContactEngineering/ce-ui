const superscriptMap: { [key: string]: string } = {
    '0': '⁰',
    '1': '¹',
    '2': '²',
    '3': '³',
    '4': '⁴',
    '5': '⁵',
    '6': '⁶',
    '7': '⁷',
    '8': '⁸',
    '9': '⁹',
    '+': '⁺',
    '-': '⁻',
    '.': '⋅',
};

/**
 * Convert numerals inside a string into the unicode superscript equivalent, e.g.
 *   µm3 => µm³
 */
export function unicodeSuperscript(s: string): string {
    return s.split('').map(c => superscriptMap[c] ?? c).join('');
}

/**
 * Format a number in exponential notation with no more than
 * `maxNumberOfDecimalPlaces` decimal places. Exponentials are displayed
 * human readably, i.e. 1.3×10³.
 *
 * @param d The number to be formatted.
 * @param maxNumberOfDecimalPlaces The number of decimal places to show (default 3).
 * @returns The formatted number.
 */
export function formatExponential(d: number, maxNumberOfDecimalPlaces: number = 3): string {
    if (typeof d !== "number" || d === 0 || isNaN(d) || !isFinite(d)) {
        return String(d);
    }

    const multiplier = Math.pow(10, maxNumberOfDecimalPlaces);
    const sign = d < 0 ? -1 : 1;
    let e = Math.floor(Math.log(sign * d) / Math.log(10));
    const m = sign * d / Math.pow(10, e);
    let mRounded = Math.round(m * multiplier) / multiplier;
    if (mRounded === 10) {
        mRounded = 1;
        e++;
    }
    if (e === 0) {
        return String(sign * mRounded);  // do not attach ×10⁰ == 1
    }
    const exponent = "10" + unicodeSuperscript(String(e));
    if (mRounded === 1) {
        return sign > 0 ? exponent : "-" + exponent;
    }
    return String(sign * mRounded) + "×" + exponent;
}

/**
 * Choose the labels for one axis, given the labels its plain formatter
 * produced.
 *
 * Bokeh formats ticks as plain decimals while they stay inside
 * [10⁻³, 10⁵] and switches to e-notation (`1.0e-6`) outside it. Plain decimals
 * are the more readable of the two and are left untouched; only the
 * e-notation case is replaced by `formatExponential`.
 *
 * The decision is made for the whole tick set rather than per tick, so that a
 * single axis never mixes the two notations.
 *
 * @param ticks The tick values.
 * @param plainLabels The labels produced for them by Bokeh's own formatter.
 * @returns The labels to display.
 */
export function preferExponentialLabels(ticks: number[], plainLabels: string[]): string[] {
    const needsExponential = plainLabels.some(label => label.includes("e") || label.includes("E"));
    return needsExponential ? ticks.map(tick => formatExponential(tick)) : plainLabels;
}

/**
 * Format bytes as human-readable text, e.g. 1.21 kB.
 *
 * @param size Number of bytes.
 * @returns Formatted string.
 */
export function prettyBytes(size: number): string {
    if (typeof size !== "number" || isNaN(size) || size < 0) {
        return String(size);
    }
    const units = ['B', 'kB', 'MB', 'GB', 'TB'];
    const i = size === 0 ? 0 : Math.min(units.length - 1, Math.floor(Math.log(size) / Math.log(1024)));
    // parseFloat drops trailing zeros, e.g. "1.00" => 1
    return `${parseFloat((size / Math.pow(1024, i)).toFixed(2))} ${units[i]}`;
}

/**
 * Format a number rounded to `significantDigits` significant figures, dropping
 * trailing zeros and never using exponential notation. Used to show a physical
 * size compactly when not editing, e.g. 9.9999999 => "10", 6.3062809 => "6.306".
 *
 * @param value The number to format.
 * @param significantDigits Number of significant figures (default 4).
 * @returns The formatted number as a string.
 */
export function formatSignificant(value: number, significantDigits: number = 4): string {
    if (value == null || typeof value !== "number" || isNaN(value) || !isFinite(value)) {
        return String(value);
    }
    if (value === 0) {
        return "0";
    }
    // toPrecision may yield exponential form; parseFloat converts back to a
    // plain decimal number and drops trailing zeros.
    return `${parseFloat(value.toPrecision(significantDigits))}`;
}

/** Shown wherever a duration or time stamp is absent. */
const MISSING = "–";

/**
 * Matches the way Django renders a `timedelta`: `[-][DD ]HH:MM:SS[.ffffff]`,
 * which is what a DRF `DurationField` puts into the JSON.
 */
const DURATION_PATTERN = /^(-?)(?:(\d+)\s)?(\d+):(\d{2}):(\d{2}(?:\.\d+)?)$/;

/**
 * Number of seconds in a duration as it arrives from the API.
 *
 * Durations come in two shapes: the staff dashboard computes them itself and
 * sends a number of seconds, while a serialized `timedelta` arrives as the
 * string Django renders it as.
 *
 * @param value Seconds, or a Django duration string.
 * @returns The duration in seconds, or `null` if there is none (a task that has
 *     not finished has no duration) or the string does not parse.
 */
export function durationSeconds(value: number | string | null | undefined): number | null {
    if (typeof value === "number") {
        return isFinite(value) ? value : null;
    }
    if (typeof value !== "string") {
        return null;
    }
    const match = DURATION_PATTERN.exec(value.trim());
    if (match == null) {
        return null;
    }
    const [, sign, days, hours, minutes, seconds] = match;
    const total = (days == null ? 0 : Number(days)) * 86400
        + Number(hours) * 3600 + Number(minutes) * 60 + Number(seconds);
    return sign === "-" ? -total : total;
}

/**
 * Format a duration for display, e.g. "< 1 sec", "42 sec", "7 min" or
 * "10 h 31 min".
 *
 * The resolution is deliberately coarse: seconds only carry information for a
 * task that finishes in under a minute, and a task measured in hours is not
 * described any better by naming its seconds. Nothing is padded, so no unit
 * ever shows a leading zero.
 *
 * @param value Seconds, or a Django duration string (see `durationSeconds`).
 * @returns The formatted duration, or a dash if there is none.
 */
export function formatDuration(value: number | string | null | undefined): string {
    const seconds = durationSeconds(value);
    if (seconds == null || seconds < 0) {
        return MISSING;
    }
    if (seconds < 1) {
        return "< 1 sec";
    }
    if (seconds < 60) {
        // Truncate rather than round, so that a duration never displays as the
        // next unit up ("60 sec").
        return `${Math.floor(seconds)} sec`;
    }
    if (seconds < 3600) {
        return `${Math.floor(seconds / 60)} min`;
    }
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return minutes === 0 ? `${hours} h` : `${hours} h ${minutes} min`;
}

/**
 * Format a fraction in [0, 1] as a percentage, e.g. 0.07 => "7%".
 *
 * Kept to two significant digits: the exact share of undefined pixels in a
 * measurement carries no more information than its order of magnitude, and a
 * share far below a percent should still read as something other than "0%".
 *
 * @param fraction The fraction to format.
 * @returns The formatted percentage, or `null` for a missing or non-finite
 *     value (a measurement that has not been inspected has no fraction).
 */
export function formatPercentage(fraction: number | null | undefined): string | null {
    if (typeof fraction !== "number" || !isFinite(fraction)) {
        return null;
    }
    if (fraction > 0 && fraction < 0.0001) {
        // Two significant digits would render this as "0%", which reads as
        // "none" rather than "very little".
        return "< 0.01%";
    }
    return `${formatSignificant(100 * fraction, 2)}%`;
}

/**
 * Format a date-time string into a human-readable local date-time string.
 *
 * @param dateTimeString The date-time string to be formatted.
 * @returns The formatted local date-time string, or `null` for missing or
 *     unparseable input (e.g. a task that never started has no start time).
 */
export function formatDateTime(dateTimeString: string | null | undefined): string | null {
    if (dateTimeString == null) {
        return null;
    }
    const date = new Date(dateTimeString);
    return isNaN(date.getTime()) ? null : date.toLocaleString();
}
