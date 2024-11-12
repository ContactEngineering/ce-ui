<script setup>

import axios from "axios";
import {onMounted, ref} from "vue";

import {
    BAlert,
    BAvatar,
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
    <BOffcanvas v-model="visible" placement="end" title="Notifications"
                footer-class="offcanvas-header">
        <template #footer>
            <BNavbarNav class="justify-content-end flex-grow-1 pe-3 mb-3">
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
            <BListGroupItem v-for="message in messages" :href="message.data.href">
                <BAvatar class="me-2"><i class="fa fa-envelope" aria-hidden="true"></i>
                </BAvatar>
                {{ message.description }}
            </BListGroupItem>
        </BListGroup>
    </BOffcanvas>
</template>