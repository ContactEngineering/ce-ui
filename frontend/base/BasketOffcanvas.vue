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

const visible = defineModel("visible", {type: Boolean, required: true});
const items = defineModel("items", {type: Object, default: {}});

onMounted(() => {
    //eventHub.on("basket:add", addItem);
    //eventHub.on("basket:remove", removeItem);
});

function clearSelection() {
    items.value = {};
}

function addItem(item) {
    items.value[item.id] = item;
}

function removeItem(item) {
    delete items.value[item.id];
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
                          :disabled="items.length === 0">
                    Clear selection
                </BNavItem>
            </BNavbarNav>
        </template>

        <BAlert :model-value="items.length === 0" variant="light">
            You have not selected any datasets.
        </BAlert>
        <BListGroup>
            <BListGroupItem v-for="item in items">
                <i class="fa fa-layer-group"></i> {{ item.name }}
            </BListGroupItem>
        </BListGroup>
    </BOffcanvas>
</template>