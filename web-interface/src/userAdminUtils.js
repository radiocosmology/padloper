/**
 * Small helpers shared by the user and user group management pages.
 */

/** Return a copy of `items` sorted by their `name`, case-insensitively. */
export function sortByName(items) {
    return (items || []).slice().sort((a, b) =>
        String(a.name).localeCompare(String(b.name), undefined,
                                     { sensitivity: 'base' }));
}

/** The union of the permissions of the groups `user` belongs to, sorted. */
export function effectivePermissions(user) {
    const perms = new Set();
    (user && user.groups ? user.groups : []).forEach((group) => {
        (group.permissions || []).forEach((perm) => perms.add(perm));
    });
    return Array.from(perms).sort();
}

/** Link target of the edit page for a user. */
export function userEditPath(name) {
    return `/manage/user/${encodeURIComponent(name)}`;
}

/** Link target of the edit page for a user group. */
export function groupEditPath(name) {
    return `/manage/group/${encodeURIComponent(name)}`;
}

/** The group whose members administer users and groups. */
export const ADMIN_GROUP = 'admin';
