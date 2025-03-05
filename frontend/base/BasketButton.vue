<script setup>

import {computed, ref} from "vue";
import {BBadge, BNavbarNav, BNavItem} from "bootstrap-vue-next";

import BasketOffcanvas from "./BasketOffcanvas.vue";

const props = defineProps({
    apiUrl: String
});

const _offcanvasVisible = ref(false);
const _items = ref({});

const nbItems = computed(() => Object.keys(_items.value).length);

</script>

<template>
    <BNavbarNav @click="_offcanvasVisible = true" class="position-relative">
        <BNavItem>
            <i class="fa fa-check-square fa-fw" aria-hidden="true"></i>
        </BNavItem>
        <BBadge v-if="nbItems > 0" variant="info" placement="top-end">
            {{ nbItems }}
            <span class="visually-hidden">items</span>
        </BBadge>
    </BNavbarNav>
    <BasketOffcanvas
        v-model:visible="_offcanvasVisible"
        v-model:items="_items"
        :api-url="apiUrl"
    ></BasketOffcanvas>
</template>