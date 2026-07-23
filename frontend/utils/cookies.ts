/**
 * Extract the value of a named cookie from a cookie string.
 *
 * @param cookieString Cookie string in `document.cookie` format.
 * @param name Name of the cookie.
 * @returns The decoded cookie value or `null` if the cookie is not present.
 */
export function getCookieFromString(cookieString: string, name: string): string | null {
    const cookie = cookieString
        .split('; ')
        .find((row) => row.startsWith(`${name}=`));

    if (cookie === undefined) {
        return null;
    }

    return decodeURIComponent(cookie.split('=').slice(1).join('='));
}

/**
 * Extract the value of a named cookie from `document.cookie`.
 */
export function getCookie(name: string): string | null {
    return getCookieFromString(document.cookie, name);
}
