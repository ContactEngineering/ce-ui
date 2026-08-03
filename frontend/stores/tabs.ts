import {computed, type WritableComputedRef} from "vue";
import {defineStore} from "pinia";

/**
 * Which tab is open on each of the tabbed pages.
 *
 * A reload re-mounts the Vue app from scratch, so the tab a user was looking at
 * is otherwise lost and they land back on the first tab — including when they
 * reload a page they had navigated deep into. This store is persisted to local
 * storage, which survives the reload, whereas component state would not.
 *
 * Entries are keyed by the *kind* of page rather than by the object shown on
 * it. That keeps the number of entries bounded, and looking at the same tab
 * again while stepping through several measurements is usually what one wants.
 */
export const useTabStore = defineStore("tabs", {
    state: () => ({
        // Tab ids, keyed by page. A page that is missing here falls back to
        // showing its first tab.
        activeTabs: {} as { [pageKey: string]: string }
    }),
    persist: true
});

/**
 * Two-way binding for the active tab of a tabbed page, to be used as the
 * `v-model` of a `BTabs`.
 *
 * `BTabs` identifies the active tab by id, so every `BTab` under it needs an
 * explicit `id`. Ids are stable across releases, while positions are not: tabs
 * get inserted, and some are only rendered for certain datasets (a dataset that
 * is published has no "Permissions" tab). Restoring by position would open a
 * different tab in those cases.
 *
 * A stored id that no tab matches — a tab that has been renamed, or one that is
 * not rendered for this object — leaves `BTabs` at its default first tab.
 *
 * @param pageKey Identifies the tab bar, e.g. "dataset-detail".
 * @returns The id of the active tab, writable.
 */
export function useActiveTab(pageKey: string): WritableComputedRef<string | undefined> {
    const tabs = useTabStore();
    return computed({
        get(): string | undefined {
            return tabs.activeTabs[pageKey];
        },
        set(id: string | undefined) {
            if (id == null) {
                delete tabs.activeTabs[pageKey];
            } else {
                tabs.activeTabs[pageKey] = id;
            }
        }
    });
}
