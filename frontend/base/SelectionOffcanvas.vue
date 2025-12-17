<script setup lang="ts">

import {
    QMenu,
    QBtn,
    QIcon,
    QList,
    QItem,
    QItemSection,
    QItemLabel,
    QSeparator,
    ClosePopup
} from "quasar";

import { useNotify } from "@/utils/notify";
import { managerApiSurfaceRetrieve } from "@/api";
import { useDatasetSelectionStore } from "@/stores/datasetSelection";
import { onMounted, ref, computed } from "vue";

const { show } = useNotify();

const selection = useDatasetSelectionStore();

const visible = defineModel("visible", { type: Boolean, required: true });

// Directive for v-close-popup
const vClosePopup = ClosePopup;

const props = defineProps({
    analysisListUrl: {
        type: String,
        default: "/ui/analysis-list/"
    }
});

const datasets = ref([]);

onMounted(async () => {
    await refreshDatasets();
    selection.$subscribe(async () => {
        await refreshDatasets();
    });
});

async function refreshDatasets() {
    datasets.value = (await Promise.all(selection.datasetIds.map(async (id) => {
        return managerApiSurfaceRetrieve({path: {id}});
    }))).map(response => {
        return response.data;
    });
}

function showCollectionInfo() {
    let issue = "";
    if (!selectionIsPublished.value) {
        issue = " Your selection contains unpublished datasets."
    }
    else if (selection.nbSelected < 2) {
        issue = " You selected less than 2 datasets."
    }
    show?.({
        props: {
            title: "Creating a collection",
            body: "To create a collection you must select at least 2, published datasets." + issue,
            variant: 'info'
        }
    });
}

const selectionIsPublished = computed(() => {
    return datasets.value.every((surface) => surface.publication != null);
})

</script>

<template>
    <QMenu v-model="visible" anchor="bottom right" self="top right" :offset="[0, 8]">
        <div class="selection-menu">
            <div class="selection-header">
                <QIcon name="check_box" />
                <span class="selection-title">Selected datasets</span>
                <span v-if="selection.nbSelected > 0" class="selection-badge">
                    {{ selection.nbSelected }}
                </span>
            </div>

            <QSeparator />

            <div class="selection-content">
                <div v-if="selection.nbSelected === 0" class="selection-empty">
                    <QIcon name="layers" size="2rem" />
                    <span>No selection</span>
                    <span class="text-caption">Select datasets from the list to analyze or download them.</span>
                </div>

                <QList v-if="datasets.length > 0" dense>
                    <QItem v-for="dataset in datasets" :key="dataset.id" class="selection-item">
                        <QItemSection avatar>
                            <QIcon name="layers" />
                        </QItemSection>
                        <QItemSection>
                            <QItemLabel>{{ dataset.name }}</QItemLabel>
                        </QItemSection>
                    </QItem>
                </QList>
            </div>

            <QSeparator />

            <div class="selection-actions">
                <QBtn
                    color="primary"
                    label="Analyze"
                    :href="`${analysisListUrl}?subjects=${selection.selectedAsBase64}`"
                    :disable="selection.nbSelected === 0"
                    unelevated
                    class="full-width q-mb-sm"
                />
                <QBtn
                    outline
                    color="primary"
                    label="Download"
                    :href="`/manager/api/surface/${selection.selectedAsString}/download/`"
                    :disable="selection.nbSelected === 0"
                    class="full-width q-mb-sm"
                />
                <QBtn
                    v-if="selection.nbSelected > 1 && selectionIsPublished"
                    outline
                    color="primary"
                    label="Create collection"
                    :href="`/ui/dataset-collection-publish/?${datasets.map((surface) => `dataset=${surface.id}`).join('&')}`"
                    class="full-width q-mb-sm"
                />
                <QBtn
                    v-else-if="selection.nbSelected > 0"
                    outline
                    color="grey"
                    label="Create collection"
                    @click="showCollectionInfo()"
                    class="full-width q-mb-sm"
                />
                <QBtn
                    flat
                    color="negative"
                    label="Clear selection"
                    @click="selection.clear()"
                    :disable="selection.nbSelected === 0"
                    class="full-width"
                />
            </div>
        </div>
    </QMenu>
</template>

<style scoped>
.selection-menu {
    min-width: 300px;
    max-width: 400px;
    background-color: var(--md-sys-color-surface);
}

.selection-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px;
    background-color: var(--md-sys-color-surface-container);
}

.selection-title {
    flex: 1;
    font-size: var(--md-sys-typescale-title-medium-size);
    font-weight: 500;
}

.selection-badge {
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 24px;
    height: 24px;
    padding: 0 8px;
    border-radius: var(--md-sys-shape-corner-full);
    background-color: var(--md-sys-color-primary);
    color: var(--md-sys-color-on-primary);
    font-size: var(--md-sys-typescale-label-large-size);
    font-weight: 500;
}

.selection-content {
    max-height: 300px;
    overflow-y: auto;
}

.selection-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    padding: 32px 16px;
    color: var(--md-sys-color-on-surface-variant);
    text-align: center;
}

.selection-item {
    border-left: 3px solid var(--md-sys-color-primary);
}

.selection-actions {
    padding: 16px;
}

.text-caption {
    font-size: var(--md-sys-typescale-body-small-size);
    color: var(--md-sys-color-on-surface-variant);
}
</style>
