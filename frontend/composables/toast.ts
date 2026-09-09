import {useToast as useBootstrapToast} from "bootstrap-vue-next";

/**
 * `useToast`, with a lifetime.
 *
 * bootstrap-vue-next leaves a toast on screen until something dismisses it, and
 * no call site in this app passed a duration, so notices piled up in the corner
 * and stayed there for the rest of the session. A *number* in `modelValue` is
 * how `BToast` expresses "hide after this many milliseconds"; this fills one in
 * wherever the caller has not asked for something else, so every toast leaves on
 * its own.
 *
 * It lives here rather than at each of the several dozen `toast.create` calls so
 * that the timing is decided once, and so it cannot be forgotten at a new one.
 * Pass `modelValue` explicitly to override it -- `true` keeps a toast up until
 * it is dismissed, for the rare notice that has to be read.
 *
 * The Django-rendered pages do not load this bundle and raise their own toasts
 * from the same markup; the durations there are in `noapp.html` and are meant to
 * match these.
 */

/** How long a toast stays, by variant, in milliseconds. */
const DURATIONS: Record<string, number> = {
    // Long enough to read twice: these are the ones a reader has to act on, and
    // they are worth still being there when somebody looks back at the screen.
    danger: 12000,
    warning: 12000,
};

/** Everything else: long enough to notice, short enough not to be in the way. */
const DEFAULT_DURATION = 6000;

export function useToast() {
    const toast = useBootstrapToast();

    return {
        ...toast,
        create(obj?: any) {
            // Only a plain object can be amended safely; a ref is the caller
            // driving the toast themselves, so it is passed through untouched.
            if (obj !== undefined && (typeof obj !== "object" || "value" in obj)) {
                return toast.create(obj);
            }
            const props = {...(obj ?? {})} as Record<string, unknown>;
            if (props.modelValue === undefined) {
                props.modelValue =
                    DURATIONS[props.variant as string] ?? DEFAULT_DURATION;
            }
            return toast.create(props as any);
        },
    };
}
