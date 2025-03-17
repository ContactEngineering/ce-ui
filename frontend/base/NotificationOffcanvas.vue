<script setup lang="ts">

import axios from "axios";
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
const unreadCount = defineModel("unreadCount");

const props = defineProps({
    apiUrl: {
        type: String,
        default: "/inbox/notifications/api/unread_list/"
    },
    pollingInterval: {
        type: Number,
        default: 1000  // milliseconds
    },
});

const messages = ref([]);

onMounted(() => {
    setInterval(updateNotifications, props.pollingInterval);
    updateNotifications();
});

function updateNotifications() {
    axios.get(props.apiUrl)
        .then(response => {
            unreadCount.value = response.data.unread_count;
            messages.value = response.data.unread_list;
        });
}

function clearNotifications() {
    axios.get(`${props.apiUrl}?mark_as_read=true`)
        .then(response => {
            unreadCount.value = 0;
            messages.value = [];
        });
}

</script>

<template>
    <BOffcanvas v-model="visible" placement="end" footer-class="offcanvas-header">
        <template #title>
            <i class="fa fa-bell fa-fw" aria-hidden="true"></i>
            <span class="ms-2">Notifications</span>
        </template>
        <template #footer>
            <BNavbarNav class="justify-content-end flex-grow-1">
                <BNavItem class="btn btn-secondary" @click="clearNotifications"
                          :disabled="unreadCount === 0">
                    Clear notifications
                </BNavItem>
            </BNavbarNav>
        </template>

        <BAlert :model-value="unreadCount === 0" variant="light">
            You have no unread notifications.
        </BAlert>
        <BListGroup>
            <BListGroupItem v-for="message in messages" :href="message.href">
                {{ message.description }}
            </BListGroupItem>
        </BListGroup>
    </BOffcanvas>
</template>