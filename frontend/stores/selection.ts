import {defineStore} from "pinia";

export const useSelectionStore = defineStore('selection', {
    state: () => ({
        datasetIds: [],
        datasetCache: {}
    }),
    getters: {
        nbSelected(): bigint {
            return this.datasetIds.length;
        },
        base64Selected(): string {
            return btoa(JSON.stringify({surface: this.datasetIds}));
        }
    },
    actions: {
        isSelected(datasetId: bigint): boolean {
            return this.datasetIds.includes(datasetId);
        },
        select(dataset) {
            this.datasetCache[dataset.id] = dataset;
            this.datasetIds.push(dataset.id);
        },
        unselect(datasetId: bigint) {
            this.datasetIds = this.datasetIds.filter(id => id !== datasetId);
        },
        clear() {
            this.datasetIds = [];
        },
        getDataset(datasetId: bigint) {
            return this.datasetCache[datasetId];
        }
    },
    persist: true
});
