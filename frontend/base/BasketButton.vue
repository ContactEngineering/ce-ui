<script setup>

import {ref} from "vue";
import {BBadge, BNavbarNav, BNavItem} from "bootstrap-vue-next";

import BasketOffcanvas from "topobank/base/BasketOffcanvas.vue";

const props = defineProps({
    apiUrl: String
});

const offcanvasVisible = ref(false);
const itemCount = ref(0);

</script>

<template>
    <BNavbarNav @click="offcanvasVisible = true" class="position-relative">
        <BNavItem>
            <i class="fa fa-check-square fa-fw" aria-hidden="true"></i>
        </BNavItem>
        <BBadge v-if="itemCount > 0" variant="danger" placement="top-end">
            {{ itemCount }}
            <span class="visually-hidden">unread messages</span>
        </BBadge>
    </BNavbarNav>
    <BasketOffcanvas
        v-model:visible="offcanvasVisible"
        v-model:item-count="itemCount"
        :api-url="apiUrl"
    ></BasketOffcanvas>
</template>