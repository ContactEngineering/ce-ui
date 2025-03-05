<script setup>

import axios from "axios";
import mitt from "mitt";
import {onMounted, ref} from "vue";


import {
    BAlert,
    BListGroup,
    BListGroupItem,
    BNavbarNav,
    BNavItem,
    BOffcanvas
} from "bootstrap-vue-next";

const visible = defineModel("visible");
const items = defineModel("items", {type: Array, default: () => []});

const eventHub = mitt();

function clearSelection() {
  items.value = [];
}

function addItem(item) {
  items.value.push(item);
}

function removeItem(item) {
  const index = _items.value.indexOf(item);
  items.value.splice(index, 1);
}

eventHub.on("basket-add", addItem);
eventHub.on("basket-remove", removeItem);

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
                          :disabled="itemCount === 0">
                    Clear selection
                </BNavItem>
            </BNavbarNav>
        </template>

        <BAlert :model-value="items.length === 0" variant="light">
            You have not selected any datasets.
        </BAlert>
        <BListGroup>
            <BListGroupItem v-for="item in items">
                {{ item }}
            </BListGroupItem>
        </BListGroup>
    </BOffcanvas>
</template>