/**
 * Escape a string for safe interpolation into HTML (text content and
 * attribute values).
 */
export function escapeHtml(value: any): string {
    return String(value == null ? "" : value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}
