import {beforeEach, describe, expect, it} from "vitest";
import {createPinia, setActivePinia} from "pinia";

import {useActiveTab, useTabStore} from "@/stores/tabs";

describe("useActiveTab", () => {
    beforeEach(() => {
        setActivePinia(createPinia());
    });

    it("starts out undefined so BTabs falls back to its first tab", () => {
        expect(useActiveTab("dataset-detail").value).toBeUndefined();
    });

    it("remembers the tab that was set", () => {
        const activeTab = useActiveTab("dataset-detail");
        activeTab.value = "dataset-properties";
        expect(activeTab.value).toBe("dataset-properties");
        expect(useTabStore().activeTabs).toEqual({"dataset-detail": "dataset-properties"});
    });

    it("keeps the tabs of different pages apart", () => {
        const dataset = useActiveTab("dataset-detail");
        const measurement = useActiveTab("measurement-detail");
        dataset.value = "dataset-properties";
        measurement.value = "measurement-details";
        expect(dataset.value).toBe("dataset-properties");
        expect(measurement.value).toBe("measurement-details");
    });

    it("drops the entry when the tab bar reports no active tab", () => {
        const activeTab = useActiveTab("dataset-detail");
        activeTab.value = "dataset-properties";
        activeTab.value = undefined;
        expect(activeTab.value).toBeUndefined();
        expect(useTabStore().activeTabs).toEqual({});
    });

    it("shares state between two bindings of the same page", () => {
        useActiveTab("dataset-detail").value = "dataset-bandwidths";
        expect(useActiveTab("dataset-detail").value).toBe("dataset-bandwidths");
    });
});
