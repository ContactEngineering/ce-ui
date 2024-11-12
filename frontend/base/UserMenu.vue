<script setup>

import {BNav} from "bootstrap-vue-next";

import NotificationButton from "topobank/base/NotificationButton.vue";
import UserMenuButton from "topobank/base/UserMenuButton.vue";

const props = defineProps({
    isAnonymous: Boolean,
    apiUrl: String,
    adminUrl: String,
    userName: String,
    name: String,
    orcid: String,
    isStaff: Boolean
});

</script>

<template>
    <BNav class="me-3">
        <NotificationButton></NotificationButton>
        <UserMenuButton
            :api-url="apiUrl"
            :admin-url="adminUrl"
            :name="name"
            :orcid="orcid"
            :is-staff="isStaff"
        ></UserMenuButton>
    </BNav>
</template>