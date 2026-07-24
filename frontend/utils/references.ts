/**
 * Links into the open-access Contact.Engineering reference paper
 * (Röttger et al., Surf. Topogr.: Metrol. Prop. 10 (2022) 035032).
 *
 * The article page uses section anchors of the form `#stmpac860as<sec>-<sub>`
 * (e.g. `#stmpac860as4-6` for section 4.6). `paperSection` builds such a link.
 */

export const CE_PAPER_URL =
    "https://iopscience.iop.org/article/10.1088/2051-672X/ac860a";

/**
 * Build a deep link to a section of the reference paper.
 * @param anchor the section anchor, e.g. "as4-6" for section 4.6, "as5" for 5.
 */
export function paperSection(anchor: string): string {
    return `${CE_PAPER_URL}#stmpac860${anchor}`;
}
