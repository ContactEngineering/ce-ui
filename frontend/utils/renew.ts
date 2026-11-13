/* Renewing (re-running) an analysis from its task row. */

export const SIGN_IN_TO_RENEW = "Sign in to run this analysis again";

/* What to tell the user when renewing failed. Only signed-in users may renew,
   so a 403 gets a message they can act on instead of "Request failed with
   status code 403". */
export function renewErrorMessage(error: any): string {
    const status = error?.response?.status;
    if (status === 401 || status === 403) {
        return "Only signed-in users can run an analysis again. Please sign in.";
    }
    return error?.message ?? String(error);
}
