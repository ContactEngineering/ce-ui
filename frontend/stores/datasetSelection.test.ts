import {beforeEach, describe, expect, it} from "vitest";
import {createPinia, setActivePinia} from "pinia";

import {useDatasetSelectionStore} from "@/stores/datasetSelection";

/** A dataset as the list endpoint returns it, reduced to what the store keeps. */
function dataset(id: number, name = `Dataset ${id}`) {
    return {id, name, url: `/manager/v2/surface/${id}/`};
}

describe("useDatasetSelectionStore", () => {
    beforeEach(() => {
        setActivePinia(createPinia());
    });

    it("starts empty", () => {
        const selection = useDatasetSelectionStore();

        expect(selection.datasetIds).toEqual([]);
        expect(selection.nbSelected).toBe(0);
        expect(selection.isSelected(1)).toBe(false);
    });

    it("remembers the datasets that were selected", () => {
        const selection = useDatasetSelectionStore();

        selection.select(dataset(7));
        selection.select(dataset(9));

        expect(selection.datasetIds).toEqual([7, 9]);
        expect(selection.nbSelected).toBe(2);
        expect(selection.isSelected(7)).toBe(true);
        expect(selection.isSelected(8)).toBe(false);
    });

    it("keeps the full dataset so a selected row needs no refetch", () => {
        const selection = useDatasetSelectionStore();

        selection.select(dataset(7, "Steel sample"));

        expect(selection.getDataset(7)).toMatchObject({id: 7, name: "Steel sample"});
        expect(selection.getDataset(8)).toBeUndefined();
    });

    it("forgets both the id and the cached dataset when one is unselected", () => {
        const selection = useDatasetSelectionStore();
        selection.select(dataset(7));
        selection.select(dataset(9));

        selection.unselect(7);

        expect(selection.datasetIds).toEqual([9]);
        expect(selection.isSelected(7)).toBe(false);
        // The cache is pruned as well, so a long session cannot grow it without
        // bound
        expect(selection.getDataset(7)).toBeUndefined();
        expect(selection.getDataset(9)).toMatchObject({id: 9});
    });

    it("leaves the selection alone when unselecting something not in it", () => {
        const selection = useDatasetSelectionStore();
        selection.select(dataset(7));

        selection.unselect(42);

        expect(selection.datasetIds).toEqual([7]);
        expect(selection.getDataset(7)).toMatchObject({id: 7});
    });

    it("drops everything on clear", () => {
        const selection = useDatasetSelectionStore();
        selection.select(dataset(7));
        selection.select(dataset(9));

        selection.clear();

        expect(selection.datasetIds).toEqual([]);
        expect(selection.nbSelected).toBe(0);
        expect(selection.getDataset(7)).toBeUndefined();
    });

    it("renders the selection as the comma-separated ids the download route takes", () => {
        const selection = useDatasetSelectionStore();

        selection.select(dataset(3));
        expect(selection.selectedAsString).toBe("3");

        selection.select(dataset(5));
        selection.select(dataset(11));
        // `/manager/v2/download-surface/<ids>/` is built from this
        expect(selection.selectedAsString).toBe("3,5,11");
    });

    it("encodes the selection as the subjects payload the analysis page decodes", () => {
        const selection = useDatasetSelectionStore();
        selection.select(dataset(3));
        selection.select(dataset(5));

        const decoded = JSON.parse(atob(selection.selectedAsBase64));

        expect(decoded).toEqual({surface: [3, 5]});
    });

    it("encodes an empty selection without failing", () => {
        const selection = useDatasetSelectionStore();

        expect(JSON.parse(atob(selection.selectedAsBase64))).toEqual({surface: []});
        expect(selection.selectedAsString).toBe("");
    });
});
