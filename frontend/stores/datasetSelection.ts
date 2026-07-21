import {defineStore} from "pinia";

export const useDatasetSelectionStore = defineStore('selection', {
    state: () => ({
        datasetIds: [],
        datasetCache: {}
    }),
    getters: {
        nbSelected(): bigint {
            return this.datasetIds.length;
        },
        selectedAsBase64(): string {
            return btoa(JSON.stringify({surface: this.datasetIds}));
        },
        selectedAsString(): any[] {
            return this.datasetIds.join(',');
        }
    },
    actions: {
        isSelected(datasetId: number): boolean {
            return this.datasetIds.includes(datasetId);
        },
        select(dataset: any) {
            this.datasetCache[dataset.id] = dataset;
            this.datasetIds.push(dataset.id);
        },
        unselect(datasetId: number) {
            this.datasetIds = this.datasetIds.filter(
                (id: number): boolean => id !== datasetId
            );
            // Also prune the cache so it does not grow unbounded
            delete this.datasetCache[datasetId];
        },
        clear() {
            this.datasetIds = [];
            this.datasetCache = {};
        },
        getDataset(datasetId: number) {
            return this.datasetCache[datasetId];
        }
    },
    persist: true
});
