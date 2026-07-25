import {CustomJSTickFormatter} from "@bokeh/bokehjs";

import {formatExponential, preferExponentialLabels} from "@/utils/formatting";

/**
 * Bokeh's formatter for linear axes. It renders plain decimals inside
 * [10⁻³, 10⁵] and e-notation (`1.0e-6`) outside it, so it is worth delegating
 * to and correcting rather than replacing outright.
 */
const BASIC_TICK_FORMATTER = "BasicTickFormatter";

/**
 * Bokeh's formatter for log axes. It renders whole decades as `10^-9` and
 * falls back to the linear formatter's e-notation as soon as the ticks are not
 * whole decades, which happens once an axis spans less than one decade.
 * `formatExponential` covers both cases, so this one is replaced outright.
 */
const LOG_TICK_FORMATTER = "LogTickFormatter";

/**
 * Build the replacement formatter for an axis currently formatted by
 * `original`.
 *
 * Linear axes keep Bokeh's own labels — including its choice of precision —
 * whenever those are plain decimals. The formatter is invoked once per tick
 * with `this` bound to a cache object that BokehJS creates fresh for each tick
 * set, so the labels for the whole set are computed once and reused.
 *
 * @param original The formatter currently installed on the axis.
 * @param isLog Whether that formatter is the log one.
 * @returns A formatter that never emits e-notation.
 */
function exponentialTickFormatter(original, isLog: boolean): CustomJSTickFormatter {
    if (isLog) {
        return new CustomJSTickFormatter({
            code: "return formatExponential(tick);",
            args: {formatExponential: formatExponential}
        });
    }
    return new CustomJSTickFormatter({
        code: `
            if (this.labels == null) {
                this.labels = preferExponentialLabels(ticks, original.doFormat(ticks, {loc: 0}));
            }
            return this.labels[index];
        `,
        // BokehJS passes `args` through as arguments of the compiled function,
        // so plain functions and model instances can be injected into the
        // code's scope. (Only client-side: this would not survive
        // serialization from Python.)
        args: {preferExponentialLabels: preferExponentialLabels, original: original}
    });
}

/**
 * Replace the tick formatter on every numeric axis of `figure`, so that no axis
 * on the site falls back to e-notation.
 *
 * Axes with any other formatter — categorical, datetime, or one a caller set
 * deliberately — are left alone. Each axis gets its own formatter instance, so
 * that overriding one axis afterwards cannot affect the others.
 */
function useExponentialTickFormatters(figure): void {
    for (const axis of [...figure.xaxes, ...figure.yaxes]) {
        // `type` is the qualified model name; for built-in models that is just
        // the class name, but take the last segment in case of a module prefix.
        const name = axis.formatter?.type?.split(".").pop();
        if (name === BASIC_TICK_FORMATTER || name === LOG_TICK_FORMATTER) {
            axis.formatter = exponentialTickFormatter(axis.formatter, name === LOG_TICK_FORMATTER);
        }
    }
}

export function applyDefaultBokehStyle(figure) {
    figure.xaxis.axis_label_text_font_style = "normal";
    figure.yaxis.axis_label_text_font_style = "normal";
    figure.xaxis.major_label_text_font_size = "16px";
    figure.yaxis.major_label_text_font_size = "16px";
    figure.xaxis.axis_label_text_font_size = "16px";
    figure.yaxis.axis_label_text_font_size = "16px";
    useExponentialTickFormatters(figure);
}
