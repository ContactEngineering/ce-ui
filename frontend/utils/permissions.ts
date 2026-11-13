/* Rows of the dataset permissions panel (DatasetPermissions / PermissionRow). */

export interface UserSummary {
    url: string;
    name?: string;
    orcid?: string | null;  // undefined: not known yet; null: user has no ORCID iD
}

export interface PermissionRowData {
    user: string;  // URL of the user, which is what the grant/revoke API takes
    permission: string;
    isCurrentUser?: boolean;
    userData?: UserSummary;  // what is already known about the user, if anything
}

/* A row from an entry of a permission set's `user_permissions`. That entry
   embeds the user's url and name, so the row can be shown without another
   request. */
export function rowFromUserPermission(p: {
    user: UserSummary;
    allow: string;
    is_current_user?: boolean;
}): PermissionRowData {
    return {
        user: p.user.url,
        permission: p.allow,
        isCurrentUser: p.is_current_user,
        userData: p.user
    };
}

/* A row for a user picked in the user search, which returns the full user.
   Keeping it matters: a user found by exact name or ORCID iD is not visible
   through the user API until the dataset is actually shared with them. */
export function rowForNewUser(user: UserSummary, permission = "view"): PermissionRowData {
    return {user: user.url, permission, userData: user};
}

/* Whether the row must fetch the user from the API to show name and ORCID iD. */
export function needsUserDetails(row: PermissionRowData): boolean {
    return row.userData?.name == null || row.userData.orcid === undefined;
}
