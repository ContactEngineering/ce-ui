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
