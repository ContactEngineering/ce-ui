<script setup>

import {ref} from "vue";
import {BNav} from "bootstrap-vue-next";

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
    <a class="nav-link me-3" id="user-dropdown" role="button"
       @click="offcanvasVisible = !offcanvasVisible">
        <i class="fa fa-user-circle fa-fw" aria-hidden="true"></i>
        <span v-if="!isAnonymous" class="ms-1">{{ name }}</span>
    </a>
    <BNav>
        <UserMenuOffcanvas
            v-model:visible="offcanvasVisible"
            :api-url="apiUrl"
            :admin-url="adminUrl"
            :name="name"
            :orcid="orcid"
            :is-staff="isStaff"
        ></UserMenuOffcanvas>
    </BNav>
</template>