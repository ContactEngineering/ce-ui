<script setup>

import { ref } from "vue";
import { QBtn, QBadge } from "quasar";

import NotificationOffcanvas from "topobank/base/NotificationOffcanvas.vue";

const props = defineProps({
    apiUrl: String
});

const offcanvasVisible = ref(false);
const unreadCount = ref(0);

</script>

<template>
    <QBtn flat round @click="offcanvasVisible = true" class="text-white">
        <i class="fa fa-bell fa-fw" aria-hidden="true"></i>
        <QBadge v-if="unreadCount > 0" color="negative" floating>
            {{ unreadCount }}
        </QBadge>
    </QBtn>
    <NotificationOffcanvas
        v-model:visible="offcanvasVisible"
        v-model:unread-count="unreadCount"
        :api-url="apiUrl"
    ></NotificationOffcanvas>
</template>