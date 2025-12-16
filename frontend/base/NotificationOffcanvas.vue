<script setup lang="ts">

// NOTE: This component uses axios directly because the notification API endpoint
// (/inbox/notifications/api/unread_list/) is not in the OpenAPI schema.
// Consider updating the backend OpenAPI schema to include this endpoint.
import axios from "axios";
import { onMounted, ref } from "vue";

import {
    QDrawer,
    QToolbar,
    QToolbarTitle,
    QBtn,
    QList,
    QItem,
    QItemSection,
    QBanner
} from "quasar";

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
    <QDrawer v-model="visible" side="right" :width="300" bordered overlay>
        <div class="column full-height">
            <QToolbar class="bg-primary text-white">
                <i class="fa fa-bell fa-fw q-mr-sm" aria-hidden="true"></i>
                <QToolbarTitle>Notifications</QToolbarTitle>
                <QBtn flat round icon="close" @click="visible = false" />
            </QToolbar>

            <div class="col q-pa-md">
                <QBanner v-if="unreadCount === 0" class="bg-grey-2 q-mb-md">
                    You have no unread notifications.
                </QBanner>
                <QList bordered separator v-if="messages.length > 0">
                    <QItem v-for="message in messages" :key="message.href" clickable :href="message.href">
                        <QItemSection>{{ message.description }}</QItemSection>
                    </QItem>
                </QList>
            </div>

            <QToolbar class="bg-grey-2">
                <QBtn
                    color="secondary"
                    label="Clear notifications"
                    @click="clearNotifications"
                    :disable="unreadCount === 0"
                    class="full-width"
                />
            </QToolbar>
        </div>
    </QDrawer>
</template>