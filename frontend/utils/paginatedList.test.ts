import {afterEach, beforeEach, describe, expect, it, vi} from "vitest";
import {nextTick} from "vue";

const {mockGet} = vi.hoisted(() => ({mockGet: vi.fn()}));

vi.mock("axios", () => ({
    default: {
        get: mockGet,
        // The composable asks axios whether a rejection is an abort; mirror
        // that with a marker the tests can attach.
        isCancel: (error: any) => error?.__cancel === true
    }
}));

import {formatBytes, formatTimestamp, usePaginatedList} from "@/utils/paginatedList";

/** A promise whose settlement the test controls, standing in for a request. */
function deferred() {
    let resolve!: (value: any) => void;
    let reject!: (error: any) => void;
    const promise = new Promise((res, rej) => {
        resolve = res;
        reject = rej;
    });
    return {promise, resolve, reject};
}

/** Let the composable's `.then`/`.catch` handler run before asserting.
 *
 * Both handlers are attached to `promise` before this one, so FIFO ordering of
 * the microtask queue guarantees they have run once this resolves.
 */
async function settled(promise: Promise<any>) {
    await promise.catch(() => undefined);
    await nextTick();
}

/** The query string of the n-th request the composable issued. */
function requestUrl(index: number): string {
    return mockGet.mock.calls[index][0] as string;
}

describe("usePaginatedList", () => {
    beforeEach(() => {
        mockGet.mockReset();
        mockGet.mockReturnValue(deferred().promise);
        // The composable registers `onBeforeUnmount`, which warns when it is
        // called outside a component instance. Exercising it directly is the
        // point here, so the expected warning is silenced rather than printed.
        vi.spyOn(console, "warn").mockImplementation(() => undefined);
    });

    afterEach(() => {
        vi.useRealTimers();
        vi.restoreAllMocks();
    });

    it("requests the slice that the offset asks for", () => {
        const list = usePaginatedList("/api/things");

        list.load(50);

        expect(mockGet).toHaveBeenCalledTimes(1);
        expect(requestUrl(0)).toContain("offset=50");
        expect(requestUrl(0)).toContain("limit=25");
        // Third page of 25, counted from one, is what the pager displays
        expect(list.currentPage.value).toBe(3);
        expect(list.isLoading.value).toBe(true);
    });

    it("translates a page number into an offset", () => {
        const list = usePaginatedList("/api/things", {pageSize: 10});

        list.goToPage(4);

        expect(requestUrl(0)).toContain("offset=30");
        expect(requestUrl(0)).toContain("limit=10");
        expect(list.currentPage.value).toBe(4);
    });

    it("publishes the rows and the total from the response", async () => {
        const request = deferred();
        mockGet.mockReturnValue(request.promise);
        const list = usePaginatedList("/api/things");

        list.load();
        request.resolve({data: {results: [{id: 1}, {id: 2}], count: 7}});
        await settled(request.promise);

        expect(list.items.value).toEqual([{id: 1}, {id: 2}]);
        expect(list.count.value).toBe(7);
        expect(list.isLoading.value).toBe(false);
        expect(list.errorMessage.value).toBeNull();
    });

    it("omits ordering and search when there is nothing to send", () => {
        const list = usePaginatedList("/api/things");

        list.load();

        expect(requestUrl(0)).not.toContain("ordering");
        expect(requestUrl(0)).not.toContain("search");
    });

    it("sends the ordering it was configured with", () => {
        const list = usePaginatedList("/api/things", {ordering: "name"});

        list.load();

        expect(requestUrl(0)).toContain("ordering=name");
    });

    it("flips the direction when the same column is sorted twice", () => {
        const list = usePaginatedList("/api/things", {ordering: "name"});

        list.sortBy("name");
        expect(list.ordering.value).toBe("-name");
        expect(requestUrl(0)).toContain("ordering=-name");

        list.sortBy("name");
        expect(list.ordering.value).toBe("name");
        expect(requestUrl(1)).toContain("ordering=name");
    });

    it("starts ascending when a different column is sorted", () => {
        const list = usePaginatedList("/api/things", {ordering: "-name"});

        list.sortBy("size");

        expect(list.ordering.value).toBe("size");
        expect(requestUrl(0)).toContain("ordering=size");
    });

    it("appends extra parameters, repeating keys for list values", () => {
        const list = usePaginatedList("/api/things", {
            extraParams: () => ({task_state: ["pe", "st"], kind: "task"})
        });

        list.load();

        const url = requestUrl(0);
        expect(url).toContain("task_state=pe");
        expect(url).toContain("task_state=st");
        expect(url).toContain("kind=task");
    });

    it("coalesces a burst of keystrokes into a single request", async () => {
        vi.useFakeTimers();
        const list = usePaginatedList("/api/things", {searchDelay: 300});

        for (const term of ["a", "ab", "abc"]) {
            list.searchTerm.value = term;
            await nextTick();
        }
        expect(mockGet).not.toHaveBeenCalled();

        vi.advanceTimersByTime(300);

        expect(mockGet).toHaveBeenCalledTimes(1);
        expect(requestUrl(0)).toContain("search=abc");
    });

    it("searches for the trimmed term, and not at all for blank input", async () => {
        vi.useFakeTimers();
        const list = usePaginatedList("/api/things", {searchDelay: 300});

        list.searchTerm.value = "  steel  ";
        await nextTick();
        vi.advanceTimersByTime(300);
        expect(requestUrl(0)).toContain("search=steel");

        list.searchTerm.value = "   ";
        await nextTick();
        vi.advanceTimersByTime(300);
        expect(requestUrl(1)).not.toContain("search=");
    });

    it("reloads when the page size changes", async () => {
        const list = usePaginatedList("/api/things");

        list.pageSize.value = 50;
        await nextTick();

        expect(mockGet).toHaveBeenCalledTimes(1);
        expect(requestUrl(0)).toContain("limit=50");
    });

    it("aborts the request still in flight", () => {
        const signals: AbortSignal[] = [];
        mockGet.mockImplementation((_url: string, config: any) => {
            signals.push(config.signal);
            return deferred().promise;
        });
        const list = usePaginatedList("/api/things");

        list.load(0);
        list.load(25);

        expect(signals[0].aborted).toBe(true);
        expect(signals[1].aborted).toBe(false);
    });

    it("never lets a superseded response overwrite a newer one", async () => {
        const first = deferred();
        const second = deferred();
        mockGet.mockReturnValueOnce(first.promise).mockReturnValueOnce(second.promise);
        const list = usePaginatedList("/api/things");

        list.load(0);
        list.load(25);

        second.resolve({data: {results: [{id: "current"}], count: 1}});
        await settled(second.promise);
        expect(list.items.value).toEqual([{id: "current"}]);

        // The first request comes back late; its rows are stale by now.
        first.resolve({data: {results: [{id: "stale"}], count: 99}});
        await settled(first.promise);

        expect(list.items.value).toEqual([{id: "current"}]);
        expect(list.count.value).toBe(1);
    });

    it("reports the error detail the server sent", async () => {
        const request = deferred();
        mockGet.mockReturnValue(request.promise);
        const list = usePaginatedList("/api/things");

        list.load();
        request.reject({response: {data: {detail: "Not allowed to list users."}}});
        await settled(request.promise);

        expect(list.errorMessage.value).toBe("Not allowed to list users.");
        expect(list.isLoading.value).toBe(false);
    });

    it("stays quiet when a request was aborted rather than failed", async () => {
        const request = deferred();
        mockGet.mockReturnValue(request.promise);
        const list = usePaginatedList("/api/things");

        list.load();
        request.reject({__cancel: true});
        await settled(request.promise);

        // An abort is the composable's own doing, not something to show a user
        expect(list.errorMessage.value).toBeNull();
    });

    it("does not report an error from a request that was superseded", async () => {
        const first = deferred();
        const second = deferred();
        mockGet.mockReturnValueOnce(first.promise).mockReturnValueOnce(second.promise);
        const list = usePaginatedList("/api/things");

        list.load(0);
        list.load(25);
        first.reject({response: {data: {detail: "stale failure"}}});
        await settled(first.promise);

        expect(list.errorMessage.value).toBeNull();
    });

    it("clears a previous error once a request succeeds", async () => {
        const failing = deferred();
        const succeeding = deferred();
        mockGet.mockReturnValueOnce(failing.promise).mockReturnValueOnce(succeeding.promise);
        const list = usePaginatedList("/api/things");

        list.load();
        failing.reject({response: {data: {detail: "boom"}}});
        await settled(failing.promise);
        expect(list.errorMessage.value).toBe("boom");

        list.load();
        succeeding.resolve({data: {results: [], count: 0}});
        await settled(succeeding.promise);

        expect(list.errorMessage.value).toBeNull();
    });
});

describe("formatBytes", () => {
    it("scales to a readable unit", () => {
        expect(formatBytes(512)).toBe("512 B");
        expect(formatBytes(2048)).toBe("2.0 kB");
        expect(formatBytes(5 * 1024 * 1024)).toBe("5.0 MB");
    });

    it("renders a dash when memory was not recorded", () => {
        expect(formatBytes(null)).toBe("–");
    });
});

describe("formatTimestamp", () => {
    it("renders a dash for a missing timestamp", () => {
        expect(formatTimestamp(null)).toBe("–");
    });

    it("renders a locale string for a real timestamp", () => {
        const formatted = formatTimestamp("2026-07-25T10:30:00Z");
        expect(formatted).not.toBe("–");
        expect(formatted).toContain("2026");
    });
});
