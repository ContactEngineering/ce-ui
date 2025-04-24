<script setup lang="ts">

import axios from "axios";

import {
    BAlert,
    BListGroup,
    BListGroupItem,
    BNavbarNav,
    BNavItem,
    BOffcanvas
} from "bootstrap-vue-next";

import { useDatasetSelectionStore } from "@/stores/datasetSelection";
import { onMounted, ref, computed } from "vue";

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
        return axios.get("/manager/api/surface/" + id);
    }))).map(response => {
        return response.data;
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
                <BNavItem class="btn btn-light mb-2"
                    :href="`/ui/dataset-collection-publish/?${datasets.map((surface) => `dataset=${surface.id}`).join('&')}`"
                    :disabled="selection.nbSelected <= 1 || !selectionIsPublished">
                    {{}}
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
