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
        },
        clear() {
            this.datasetIds = [];
        },
        getDataset(datasetId: number) {
            return this.datasetCache[datasetId];
        }
    },
    persist: true
});
