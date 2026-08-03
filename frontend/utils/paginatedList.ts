import axios from "axios";
import {onBeforeUnmount, ref, watch} from "vue";

/**
 * Shared fetch logic for the searchable, paginated staff dashboards.
 *
 * Search boxes fire a request per keystroke unless they are throttled, and the
 * responses can come back out of order. This debounces the query, aborts the
 * request still in flight, and tags each request with a sequence number so a
 * superseded response can never overwrite a newer one.
 */
export function usePaginatedList(apiUrl: string, options: {
    pageSize?: number,
    searchDelay?: number,
    ordering?: string,
    extraParams?: () => Record<string, string | string[]>
} = {}) {
    const pageSize = ref<number>(options.pageSize ?? 25);
    const searchDelay = options.searchDelay ?? 300;

    const items = ref<any[]>([]);
    const count = ref<number>(0);
    const currentPage = ref<number>(1);
    const isLoading = ref<boolean>(false);
    const errorMessage = ref<string | null>(null);
    const searchTerm = ref<string>("");
    // `null` means "use the server default", which for the task dashboard is
    // running-tasks-first.
    const ordering = ref<string | null>(options.ordering ?? null);

    let searchDelayTimer: ReturnType<typeof setTimeout> | null = null;
    let requestSequence = 0;
    let abortController: AbortController | null = null;

    function load(offset: number = 0) {
        const requestId = ++requestSequence;
        if (abortController != null) {
            abortController.abort();
        }
        abortController = new AbortController();
        isLoading.value = true;
        currentPage.value = Math.floor(offset / pageSize.value) + 1;

        const params = new URLSearchParams();
        params.append("offset", String(offset));
        params.append("limit", String(pageSize.value));
        if (ordering.value != null) {
            params.append("ordering", ordering.value);
        }
        if (searchTerm.value.trim().length > 0) {
            params.append("search", searchTerm.value.trim());
        }
        for (const [key, value] of Object.entries(options.extraParams?.() ?? {})) {
            for (const entry of Array.isArray(value) ? value : [value]) {
                params.append(key, entry);
            }
        }

        axios.get(`${apiUrl}?${params.toString()}`, {signal: abortController.signal})
            .then(response => {
                if (requestId !== requestSequence) {
                    return;  // superseded by a newer request
                }
                items.value = response.data.results;
                count.value = response.data.count;
                errorMessage.value = null;
                isLoading.value = false;
            })
            .catch(error => {
                if (requestId !== requestSequence || axios.isCancel(error)) {
                    return;
                }
                errorMessage.value = error.response?.data?.detail ?? String(error);
                isLoading.value = false;
            });
    }

    function goToPage(page: number) {
        load((page - 1) * pageSize.value);
    }

    function sortBy(field: string) {
        // Clicking the active column flips the direction.
        ordering.value = ordering.value === field ? `-${field}` : field;
        load();
    }

    watch(searchTerm, () => {
        if (searchDelayTimer != null) {
            clearTimeout(searchDelayTimer);
        }
        searchDelayTimer = setTimeout(() => load(), searchDelay);
    });

    watch(pageSize, () => load());

    onBeforeUnmount(() => {
        if (searchDelayTimer != null) {
            clearTimeout(searchDelayTimer);
        }
        abortController?.abort();
    });

    return {
        items, count, currentPage, pageSize, isLoading, errorMessage,
        searchTerm, ordering, load, goToPage, sortBy
    };
}

/** Format an ISO timestamp for the dashboards, or a dash if it is absent. */
export function formatTimestamp(value: string | null): string {
    if (value == null) {
        return "–";
    }
    return new Date(value).toLocaleString();
}

/** Format a byte count as a human-readable size. */
export function formatBytes(value: number | null): string {
    if (value == null) {
        return "–";
    }
    const units = ["B", "kB", "MB", "GB", "TB"];
    let size = value;
    let unit = 0;
    while (size >= 1024 && unit < units.length - 1) {
        size /= 1024;
        unit++;
    }
    return `${size.toFixed(unit === 0 ? 0 : 1)} ${units[unit]}`;
}
