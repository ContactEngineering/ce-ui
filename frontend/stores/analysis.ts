import {defineStore} from "pinia";

export const useAnalysisStore = defineStore('analysis', {
    state: () => ({
        workflows: [],
    }),
    actions: {
        isSelected(workflow: string): boolean {
            return this.workflows.includes(workflow);
        },
        select(workflow: string) {
            this.workflows.push(workflow);
        },
        unselect(workflow: string) {
            this.workflows = this.workflows.filter(
                (w: string): boolean => w !== workflow
            );
        },
        selectAll(workflows: string[]) {
            // Assign rather than push, so that selecting all does not leave
            // duplicates behind for the workflows that were already selected
            this.workflows = [...workflows];
        },
        clear() {
            this.workflows = [];
        }
    },
    persist: true
});