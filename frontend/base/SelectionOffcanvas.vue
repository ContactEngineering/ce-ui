<script setup lang="ts">

import {
    QDrawer,
    QToolbar,
    QToolbarTitle,
    QBtn,
    QList,
    QItem,
    QItemSection,
    QItemLabel,
    QBanner
} from "quasar";

import { useNotify } from "@/utils/notify";
import { managerApiSurfaceRetrieve } from "@/api";
import { useDatasetSelectionStore } from "@/stores/datasetSelection";
import { onMounted, ref, computed } from "vue";

const { show } = useNotify();

const selection = useDatasetSelectionStore();

const visible = defineModel("visible", { type: Boolean, required: true });

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
    <QDrawer v-model="visible" side="right" :width="300" bordered overlay>
        <div class="column full-height">
            <QToolbar class="bg-primary text-white">
                <i class="fa fa-check-square fa-fw q-mr-sm" aria-hidden="true"></i>
                <QToolbarTitle>Selected datasets</QToolbarTitle>
                <QBtn flat round icon="close" @click="visible = false" />
            </QToolbar>

            <div class="col q-pa-md">
                <QBanner v-if="selection.nbSelected === 0" class="bg-grey-2 q-mb-md">
                    You have not selected any datasets.
                </QBanner>
                <QList bordered separator v-if="datasets.length > 0">
                    <QItem v-for="dataset in datasets" :key="dataset.id">
                        <QItemSection avatar>
                            <i class="fa fa-layer-group"></i>
                        </QItemSection>
                        <QItemSection>
                            <QItemLabel>{{ dataset.name }}</QItemLabel>
                        </QItemSection>
                    </QItem>
                </QList>
            </div>

            <div class="q-pa-md column q-gutter-sm">
                <QBtn
                    color="positive"
                    label="Analyze"
                    :href="`${analysisListUrl}?subjects=${selection.selectedAsBase64}`"
                    :disable="selection.nbSelected === 0"
                />
                <QBtn
                    color="grey-4"
                    text-color="dark"
                    label="Download"
                    :href="`/manager/api/surface/${selection.selectedAsString}/download/`"
                    :disable="selection.nbSelected === 0"
                />
                <QBtn
                    v-if="selection.nbSelected > 1 && selectionIsPublished"
                    color="grey-4"
                    text-color="dark"
                    label="Create collection"
                    :href="`/ui/dataset-collection-publish/?${datasets.map((surface) => `dataset=${surface.id}`).join('&')}`"
                />
                <QBtn
                    v-else
                    color="grey-4"
                    text-color="dark"
                    label="Create collection"
                    @click="showCollectionInfo()"
                />
                <QBtn
                    color="secondary"
                    label="Clear selection"
                    @click="selection.clear()"
                    :disable="selection.nbSelected === 0"
                />
            </div>
        </div>
    </QDrawer>
</template>
