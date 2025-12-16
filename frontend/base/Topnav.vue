<script setup>

import { inject, onMounted } from "vue";
import { QToolbar, QToolbarTitle, QBtn, QSpace } from "quasar";

import { useNotify } from "@/utils/notify";

import NotificationButton from "./NotificationButton.vue";
import UserMenuButton from "./UserMenuButton.vue";

const { show } = useNotify();

const props = defineProps({
    messages: {
        type: Array,
        default: []
    }
});

const appProps = inject("appProps");

const levelToVariant = {
    'error': 'danger',
    'warning': 'warning',
    'info': 'info',
    'success': 'success'
};

const levelToTitle = {
    'error': 'Error',
    'warning': 'Warning',
    'info': 'Information',
    'success': 'Success'
}

onMounted(() => {
    for (const message of props.messages) {
        show?.({
            props: {
                title: levelToTitle[message.level],
                body: message.message,
                variant: levelToVariant[message.level]
            }
        });
    }
});

</script>

<template>
    <QToolbar class="topnav">
        <a href="/" class="brand-link">
            <img src="/static/images/ce_logo.svg" height="28px" alt="Logo">
            <span class="brand-text">contact.engineering</span>
        </a>
        <QSpace />
        <div v-if="appProps.userIsAnonymous">
            <QBtn
                :href="appProps.loginUrl"
                color="primary"
                unelevated
                label="Sign in"
            />
        </div>
        <NotificationButton v-if="!appProps.userIsAnonymous" />
        <UserMenuButton
            v-if="!appProps.userIsAnonymous"
            :api-url="appProps.userApiUrl"
            :admin-url="appProps.adminUrl"
            :name="appProps.userFullName"
            :orcid="appProps.userOrcid"
            :is-staff="appProps.userIsStaff"
        />
    </QToolbar>
</template>

<style scoped>
.topnav {
    background-color: var(--md-sys-color-surface);
    box-shadow: var(--md-sys-elevation-level2);
    padding: 8px 16px;
}

.brand-link {
    display: flex;
    align-items: center;
    text-decoration: none;
    color: var(--md-sys-color-on-surface);
    gap: 12px;
}

.brand-link:hover {
    color: var(--md-sys-color-primary);
}

.brand-text {
    font-size: var(--md-sys-typescale-title-medium-size);
    font-weight: 500;
    letter-spacing: 0.15px;
}
</style>