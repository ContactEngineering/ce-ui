<script setup>

import { inject, onMounted } from "vue";
import { QToolbar, QToolbarTitle, QBtn, QAvatar, QSpace } from "quasar";

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
    <QToolbar>
        <QBtn flat dense :href="'/'">
            <QAvatar square size="28px">
                <img src="/static/images/ce_logo.svg" alt="Logo">
            </QAvatar>
        </QBtn>
        <QToolbarTitle>
            contact.engineering
        </QToolbarTitle>
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
