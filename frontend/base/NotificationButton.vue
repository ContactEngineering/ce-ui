<script setup>

import { inject, onMounted, ref } from "vue";
import axios from "axios";
import { QBtn, QBadge } from "quasar";

const props = defineProps({
    apiUrl: {
        type: String,
        default: "/inbox/notifications/api/unread_list/"
    },
    pollingInterval: {
        type: Number,
        default: 5000
    }
});

const rightDrawer = inject('rightDrawer');
const unreadCount = ref(0);

onMounted(() => {
    setInterval(updateNotifications, props.pollingInterval);
    updateNotifications();
});

function updateNotifications() {
    axios.get(props.apiUrl)
        .then(response => {
            unreadCount.value = response.data.unread_count;
        });
}

function openNotifications() {
    rightDrawer.open('notifications');
}

</script>

<template>
    <QBtn flat round @click="openNotifications" icon="notifications">
        <QBadge v-if="unreadCount > 0" color="negative" floating>
            {{ unreadCount }}
        </QBadge>
    </QBtn>
</template>
