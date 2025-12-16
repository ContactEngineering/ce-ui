<script setup lang="ts">

// NOTE: This component uses axios directly because the notification API endpoint
// (/inbox/notifications/api/unread_list/) is not in the OpenAPI schema.
// Consider updating the backend OpenAPI schema to include this endpoint.
import axios from "axios";
import { onMounted, ref } from "vue";

import {
    QMenu,
    QBtn,
    QList,
    QItem,
    QItemSection,
    QSeparator,
    ClosePopup
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

// Directive for v-close-popup
const vClosePopup = ClosePopup;

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
    <QMenu v-model="visible" anchor="bottom right" self="top right" :offset="[0, 8]">
        <div class="notification-menu">
            <div class="notification-header">
                <q-icon name="notifications" />
                <span class="notification-title">Notifications</span>
                <span v-if="unreadCount > 0" class="notification-badge">{{ unreadCount }}</span>
            </div>

            <QSeparator />

            <div class="notification-content">
                <div v-if="unreadCount === 0" class="notification-empty">
                    <q-icon name="check_circle" size="2rem" />
                    <span>All caught up!</span>
                    <span class="text-caption">You have no unread notifications.</span>
                </div>

                <QList v-if="messages.length > 0" dense>
                    <QItem
                        v-for="message in messages"
                        :key="message.href"
                        clickable
                        v-close-popup
                        :href="message.href"
                        class="notification-item"
                    >
                        <QItemSection avatar>
                            <q-icon name="info" />
                        </QItemSection>
                        <QItemSection>
                            <div class="notification-text">{{ message.description }}</div>
                        </QItemSection>
                    </QItem>
                </QList>
            </div>

            <QSeparator />

            <div class="notification-footer">
                <QBtn
                    flat
                    color="primary"
                    label="Clear all"
                    @click="clearNotifications"
                    :disable="unreadCount === 0"
                    size="sm"
                    class="full-width"
                />
            </div>
        </div>
    </QMenu>
</template>

<style scoped>
.notification-menu {
    min-width: 320px;
    max-width: 400px;
    background-color: var(--md-sys-color-surface);
}

.notification-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px;
    background-color: var(--md-sys-color-surface-container);
}

.notification-title {
    flex: 1;
    font-size: var(--md-sys-typescale-title-medium-size);
    font-weight: 500;
}

.notification-badge {
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 24px;
    height: 24px;
    padding: 0 8px;
    border-radius: var(--md-sys-shape-corner-full);
    background-color: var(--md-sys-color-error);
    color: var(--md-sys-color-on-error);
    font-size: var(--md-sys-typescale-label-large-size);
    font-weight: 500;
}

.notification-content {
    max-height: 400px;
    overflow-y: auto;
}

.notification-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    padding: 32px 16px;
    color: var(--md-sys-color-on-surface-variant);
    text-align: center;
}

.notification-item {
    border-left: 3px solid var(--md-sys-color-primary);
}

.notification-text {
    font-size: var(--md-sys-typescale-body-medium-size);
    line-height: 1.4;
}

.notification-footer {
    padding: 8px 16px;
}

.text-caption {
    font-size: var(--md-sys-typescale-body-small-size);
    color: var(--md-sys-color-on-surface-variant);
}
</style>
