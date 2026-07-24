<script setup lang="ts">

import axios from "axios";
import {onBeforeUnmount, onMounted, ref} from "vue";

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

let pollingIntervalId = null;

onMounted(() => {
    pollingIntervalId = setInterval(updateNotifications, props.pollingInterval);
    updateNotifications();
});

onBeforeUnmount(() => {
    if (pollingIntervalId != null) {
        clearInterval(pollingIntervalId);
        pollingIntervalId = null;
    }
});

function updateNotifications() {
    axios.get(props.apiUrl)
        .then(response => {
            unreadCount.value = response.data.unread_count;
            messages.value = response.data.unread_list;
        })
        .catch(error => {
            // Swallow transient server errors so polling does not produce unhandled rejections
            console.error("Failed to update notifications:", error);
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
    <BOffcanvas v-model="visible" placement="end">
        <template #title>
            <i class="fa fa-bell fa-fw" aria-hidden="true"></i>
            <span class="ms-2">Notifications</span>
        </template>
        <template #footer>
            <BNavbarNav class="p-3 justify-content-end flex-grow-1">
                <BNavItem class="btn btn-secondary" @click="clearNotifications"
                          :disabled="unreadCount === 0">
                    Clear notifications
                </BNavItem>
            </BNavbarNav>
        </template>

        <BAlert :model-value="unreadCount === 0" variant="secondary">
            <i class="fa-solid fa-circle-info me-2"></i>You have no unread notifications.
        </BAlert>
        <BListGroup>
            <BListGroupItem v-for="message in messages" :href="message.href">
                {{ message.description }}
            </BListGroupItem>
        </BListGroup>
    </BOffcanvas>
</template>