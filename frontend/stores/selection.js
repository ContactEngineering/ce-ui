import {defineStore} from "pinia";

export const useSelectionStore = defineStore('selection', {
    state: () => ({
        datasetIds: [],
        datasetCache: {}
    }),
    getters: {
        nbSelected() {
            return this.datasetIds.length;
        }
    },
    actions: {
        isSelected(datasetId) {
            return this.datasetIds.includes(datasetId);
        },
        select(dataset) {
            this.datasetCache[dataset.id] = dataset;
            this.datasetIds.push(dataset.id);
        },
        unselect(datasetId) {
            this.datasetIds = this.datasetIds.filter(id => id !== datasetId);
        },
        clear() {
            this.datasetIds = [];
        },
        getDataset(datasetId) {
            return this.datasetCache[datasetId];
        }
    },
    persist: true
});
