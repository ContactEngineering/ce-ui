<script setup>

import {onMounted} from "vue";

import {
    BAlert,
    BListGroup,
    BListGroupItem,
    BNavbarNav,
    BNavItem,
    BOffcanvas
} from "bootstrap-vue-next";

import {useSelectionStore} from "topobank/stores/selection";

const selection = useSelectionStore();

const visible = defineModel("visible", {type: Boolean, required: true});

onMounted(() => {
    //eventHub.on("basket:add", addItem);
    //eventHub.on("basket:remove", removeItem);
});

function clearSelection() {
    selction.clear();
}

</script>

<template>
    <BOffcanvas v-model="visible" placement="end" footer-class="offcanvas-header">
        <template #title>
            <i class="fa fa-bell fa-fw" aria-hidden="true"></i>
            <span class="ms-2">Selected datasets</span>
        </template>
        <template #footer>
            <BNavbarNav class="justify-content-end flex-grow-1">
                <BNavItem class="btn btn-secondary" @click="clearSelection"
                          :disabled="selection.nbSelected === 0">
                    Clear selection
                </BNavItem>
            </BNavbarNav>
        </template>

        <BAlert :model-value="selection.nbSelected === 0" variant="light">
            You have not selected any datasets.
        </BAlert>
        <BListGroup>
            <BListGroupItem v-for="dataset in selection.datasetIds">
                <i class="fa fa-layer-group"></i> {{ dataset }}
            </BListGroupItem>
        </BListGroup>
    </BOffcanvas>
</template>