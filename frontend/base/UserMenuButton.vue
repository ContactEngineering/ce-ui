<script setup>

import {ref} from "vue";
import {BNavbarNav, BNavItem} from "bootstrap-vue-next";

import UserMenuOffcanvas from "topobank/base/UserMenuOffcanvas.vue";

const props = defineProps({
    isAnonymous: Boolean,
    apiUrl: String,
    adminUrl: String,
    userName: String,
    name: String,
    orcid: String,
    isStaff: Boolean
});

const offcanvasVisible = ref(false);

</script>

<template>
    <BNavbarNav>
        <BNavItem @click="offcanvasVisible = true">
            <i class="fa fa-user-circle fa-fw" aria-hidden="true"></i>
            <span v-if="!isAnonymous" class="ms-1">{{ name }}</span>
        </BNavItem>
    </BNavbarNav>
    <UserMenuOffcanvas
        v-model:visible="offcanvasVisible"
        :api-url="apiUrl"
        :admin-url="adminUrl"
        :name="name"
        :orcid="orcid"
        :is-staff="isStaff"
    ></UserMenuOffcanvas>
</template>