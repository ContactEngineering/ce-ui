import {defineStore} from "pinia";

export const useSelectionStore = defineStore('selection', {
    state: () => ({
        datasetIds: []
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
        select(datasetId) {
            this.datasetIds.push(datasetId);
        },
        unselect(datasetId) {
            this.datasetIds = this.datasetIds.filter(id => id !== datasetId);
        }
    },
    persist: true
});
