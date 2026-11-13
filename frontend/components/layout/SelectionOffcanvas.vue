<script setup lang="ts">

import axios from "axios";

import {
    BAlert,
    BButton,
    BListGroup,
    BListGroupItem,
    BOffcanvas
} from "bootstrap-vue-next";
import {useToast} from "@/composables/toast";

import DownloadModal from "@/components/ui/DownloadModal.vue";
import { useDatasetSelectionStore } from "@/stores/datasetSelection";
import { onMounted, ref, computed } from "vue";

const toast = useToast();

const selection = useDatasetSelectionStore();

const visible = defineModel("visible", { type: Boolean, required: true });

const props = defineProps({
    analysisListUrl: {
        type: String,
        default: "/ui/analysis-list/"
    }
});

const datasets = ref([]);
const _downloadModal = ref(null);

/* Download the selected datasets as a single ZIP archive. The archive is built by a Celery worker; the modal reports its
   progress and starts the download once it is ready. */
function download() {
    if (selection.nbSelected === 0) {
        return;
    }
    _downloadModal.value.download(
        `/manager/v2/download-surface/${selection.selectedAsString}/`,
        {title: "Download selected datasets"});
}

onMounted(async () => {
    await refreshDatasets();
    selection.$subscribe(async () => {
        await refreshDatasets();
    });
});

async function refreshDatasets() {
    datasets.value = (await Promise.all(selection.datasetIds.map(async (id) => {
        return axios.get("/manager/v2/surface/" + id + "/");
    }))).map(response => {
        return response.data;
    });
}

function showCollectionInfo() {
    let issue = "";
    if (!selectionIsPublished.value) {
        issue = "Your selection contains unpublished datasets."
    }
    else if (selection.nbSelected < 2) {
        issue = "You selected less than 2 datasets."
    }
    toast.create({
        title: "Creating a collection",
        body: "To create a collection you must select at least 2, published datasets." + issue,
        variant: 'info'
    })?.show();
}

const selectionIsPublished = computed(() => {
    return datasets.value.every((surface) => surface.publication != null);
})

</script>

<template>
    <BOffcanvas v-model="visible" placement="end">
        <template #title>
            <i class="fa fa-bell fa-fw" aria-hidden="true"></i>
            <span class="ms-2">Selected datasets</span>
        </template>
        <template #footer>
            <!-- Real buttons: a BNavItem styled with `btn` only reacts to clicks
                 on its inner link, not on the padding of the button it looks
                 like, and still looks enabled when disabled (topobank#1407) -->
            <div class="d-grid gap-2 p-3 flex-grow-1 align-content-end">
                <BButton variant="success"
                    :href="`${analysisListUrl}?subjects=${selection.selectedAsBase64}`"
                    :disabled="selection.nbSelected === 0">
                    Analyze
                </BButton>
                <BButton variant="light"
                    :disabled="selection.nbSelected === 0"
                    @click="download()">
                    Download
                </BButton>
                <BButton v-if="selection.nbSelected > 1 && selectionIsPublished" variant="light"
                    :href="`/ui/dataset-collection-publish/?${datasets.map((surface) => `dataset=${surface.id}`).join('&')}`">
                    Create collection
                </BButton>
                <BButton v-else variant="light" @click="showCollectionInfo()">
                    Create collection
                </BButton>
                <BButton variant="secondary" @click="selection.clear()" :disabled="selection.nbSelected === 0">
                    Clear selection
                </BButton>
            </div>
        </template>

        <BAlert :model-value="selection.nbSelected === 0" variant="secondary">
            <i class="fa-solid fa-circle-info me-2"></i>You have not selected any datasets.
        </BAlert>
        <BListGroup>
            <BListGroupItem v-for="dataset in datasets">
                <i class="fa fa-layer-group"></i>
                {{ dataset.name }}
            </BListGroupItem>
        </BListGroup>
    </BOffcanvas>
    <DownloadModal ref="_downloadModal"></DownloadModal>
</template>
