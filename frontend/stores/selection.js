import {ref} from "vue";
import {defineStore} from "pinia";

export const useSelectionStore = defineStore('selection', {
    state: () => ({
        surfaceIds: []
    }),
    getters: {
        nbSelected() {
            return this.surfaceIds.length;
        }
    },
    actions: {
        select(surfaceId) {
            this.surfaceIds.push(surfaceId);
        },
        unselect(surfaceId) {
            this.surfaceIds = this.surfaceIds.filter(id => id !== surfaceId);
        }
    },
    persist: true
});
