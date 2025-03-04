<script setup>

import {onMounted, ref} from "vue";
import {
    BButton,
    BFormInput,
    BModal,
    BNavbar,
    BNavbarBrand,
    BNavbarNav,
    BNavItem,
    BToastOrchestrator,
    useToastController
} from "bootstrap-vue-next";

import NotificationButton from "topobank/base/NotificationButton.vue";
import UserMenuButton from "topobank/base/UserMenuButton.vue";

const {show} = useToastController();

const props = defineProps({
    isAnonymous: Boolean,
    apiUrl: String,
    loginUrl: String,
    adminUrl: String,
    selectUrl: String,
    userName: String,
    name: String,
    orcid: String,
    isStaff: Boolean,
    messages: {
        type: Array,
        default: []
    }
});

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
    <BToastOrchestrator/>
    <BNavbar variant="dark" class="navbar-dark">
        <BNavbarBrand href="/" class="d-flex flex-grow-1">
            <img src="/static/images/ce_logo.svg" height="25px">
            &nbsp contact.engineering
        </BNavbarBrand>
        <BNavbarNav v-if="isAnonymous">
            <BNavItem>
                <BButton :href="loginUrl" variant="outline-secondary">
                    Sign in
                </BButton>
            </BNavItem>
        </BNavbarNav>
        <NotificationButton v-if="!isAnonymous"></NotificationButton>
        <UserMenuButton
            v-if="!isAnonymous"
            :api-url="apiUrl"
            :admin-url="adminUrl"
            :name="name"
            :orcid="orcid"
            :is-staff="isStaff"
        ></UserMenuButton>
    </BNavbar>
</template>