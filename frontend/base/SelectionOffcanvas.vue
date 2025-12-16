<script setup lang="ts">

import {
    BAlert,
    BListGroup,
    BListGroupItem,
    BNavbarNav,
    BNavItem,
    BOffcanvas,
    useToastController
} from "bootstrap-vue-next";

import {managerApiSurfaceRetrieve} from "@/api";
import { useDatasetSelectionStore } from "@/stores/datasetSelection";
import { onMounted, ref, computed } from "vue";

const { show } = useToastController();

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
    const issue = "";
    if (!selectionIsPublished.value) {
        issue = "Your selection contains unpublished datasets."
    }
    else if (selection.nbSelected < 2) {
        issue = "You selected less than 2 datasets."
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
    <BOffcanvas v-model="visible" placement="end" footer-class="offcanvas-header">
        <template #title>
            <i class="fa fa-bell fa-fw" aria-hidden="true"></i>
            <span class="ms-2">Selected datasets</span>
        </template>
        <template #footer>
            <BNavbarNav class="justify-content-end flex-grow-1">
                <BNavItem class="btn btn-success mb-2"
                    :href="`${analysisListUrl}?subjects=${selection.selectedAsBase64}`"
                    :disabled="selection.nbSelected === 0">
                    Analyze
                </BNavItem>
                <BNavItem class="btn btn-light mb-2"
                    :href="`/manager/api/surface/${selection.selectedAsString}/download/`"
                    :disabled="selection.nbSelected === 0">
                    Download
                </BNavItem>
                <BNavItem v-if="selection.nbSelected > 1 && selectionIsPublished" class="btn btn-light mb-2"
                    :href="`/ui/dataset-collection-publish/?${datasets.map((surface) => `dataset=${surface.id}`).join('&')}`">
                    Create collection
                </BNavItem>
                <BNavItem v-else class="btn btn-light mb-2" @click="showCollectionInfo()">
                    Create collection
                </BNavItem>
                <BNavItem class="btn btn-secondary" @click="selection.clear()" :disabled="selection.nbSelected === 0">
                    Clear selection
                </BNavItem>
            </BNavbarNav>
        </template>

        <BAlert :model-value="selection.nbSelected === 0" variant="light">
            You have not selected any datasets.
        </BAlert>
        <BListGroup>
            <BListGroupItem v-for="dataset in datasets">
                <i class="fa fa-layer-group"></i>
                {{ dataset.name }}
            </BListGroupItem>
        </BListGroup>
    </BOffcanvas>
</template>
