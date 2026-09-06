<script setup>

import {inject, onMounted} from "vue";
import {
    BButton,
    BNavbar,
    BNavbarBrand,
    BNavbarNav,
    BNavItem,
    useToast
} from "bootstrap-vue-next";

import NotificationButton from "@/components/layout/NotificationButton.vue";
import UserMenuButton from "@/components/layout/UserMenuButton.vue";

const toast = useToast();

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
        toast.create({
            title: levelToTitle[message.level],
            body: message.message,
            variant: levelToVariant[message.level]
        })?.show();
    }
});

</script>

<template>
    <BNavbar variant="dark" class="navbar-dark">
        <BNavbarBrand href="/" class="d-flex flex-grow-1">
            <img src="/static/images/ce_logo.svg" height="25px">
            &nbsp contact.engineering
        </BNavbarBrand>
        <BNavbarNav v-if="appProps.userIsAnonymous">
            <BNavItem>
                <BButton :href="appProps.loginUrl" variant="secondary">
                    Sign in
                </BButton>
            </BNavItem>
        </BNavbarNav>
        <NotificationButton v-if="!appProps.userIsAnonymous"></NotificationButton>
        <UserMenuButton
            v-if="!appProps.userIsAnonymous"
            :api-url="appProps.userApiUrl"
            :admin-url="appProps.adminUrl"
            :connections-url="appProps.connectionsUrl"
            :name="appProps.userFullName"
            :orcid="appProps.userOrcid"
            :is-staff="appProps.userIsStaff"
        ></UserMenuButton>
    </BNavbar>
</template>