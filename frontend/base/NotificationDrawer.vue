<script setup lang="ts">

import axios from "axios";
import { inject, onMounted, ref } from "vue";

import {
    QBtn,
    QList,
    QItem,
    QItemSection,
    QSeparator,
    QIcon,
    QToolbar,
    QToolbarTitle
} from "quasar";

const props = defineProps({
    apiUrl: {
        type: String,
        default: "/inbox/notifications/api/unread_list/"
    },
    pollingInterval: {
        type: Number,
        default: 1000
    },
});

const rightDrawer = inject('rightDrawer') as any;

const messages = ref([]);
const unreadCount = ref(0);

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
    <QToolbar class="bg-primary text-white">
        <QIcon name="notifications" size="sm" class="q-mr-sm" />
        <QToolbarTitle>Notifications</QToolbarTitle>
        <QBtn flat round dense icon="close" @click="rightDrawer.close()" />
    </QToolbar>

    <div class="q-pa-md" v-if="unreadCount === 0">
        <div class="column items-center q-py-xl text-grey-6">
            <QIcon name="check_circle" size="3rem" class="q-mb-sm" />
            <div class="text-subtitle1">All caught up!</div>
            <div class="text-caption">You have no unread notifications.</div>
        </div>
    </div>

    <QList v-if="messages.length > 0" separator>
        <QItem
            v-for="message in messages"
            :key="message.href"
            clickable
            :href="message.href"
            @click="rightDrawer.close()"
        >
            <QItemSection avatar>
                <QIcon name="info" color="primary" />
            </QItemSection>
            <QItemSection>
                <div>{{ message.description }}</div>
            </QItemSection>
        </QItem>
    </QList>

    <QSeparator v-if="messages.length > 0" />

    <div class="q-pa-md">
        <QBtn
            flat
            color="primary"
            label="Clear all"
            @click="clearNotifications"
            :disable="unreadCount === 0"
            class="full-width"
        />
    </div>
</template>
