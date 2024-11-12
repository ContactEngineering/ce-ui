<script setup>

import {ref} from "vue";
import {BBadge, BNavbarNav, BNavItem} from "bootstrap-vue-next";

import NotificationOffcanvas from "topobank/base/NotificationOffcanvas.vue";

const props = defineProps({
    apiUrl: String
});

const offcanvasVisible = ref(false);
const unreadCount = ref(0);

</script>

<template>
    <BNavbarNav @click="offcanvasVisible = true" class="position-relative">
        <BNavItem>
            <i class="fa fa-bell fa-fw" aria-hidden="true"></i>
        </BNavItem>
        <BBadge v-if="unreadCount > 0" variant="danger" placement="top-end">
            {{ unreadCount }}
            <span class="visually-hidden">unread messages</span>
        </BBadge>
    </BNavbarNav>
    <NotificationOffcanvas
        v-model:visible="offcanvasVisible"
        v-model:unread-count="unreadCount"
        :api-url="apiUrl"
    ></NotificationOffcanvas>
</template>