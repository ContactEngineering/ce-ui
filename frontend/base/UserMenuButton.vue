<script setup>

import { ref } from "vue";
import { QBtn } from "quasar";

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
    <QBtn flat @click="offcanvasVisible = true" icon="account_circle">
        <span v-if="!isAnonymous" class="q-ml-xs">{{ name }}</span>
    </QBtn>
    <UserMenuOffcanvas
        v-model:visible="offcanvasVisible"
        :api-url="apiUrl"
        :admin-url="adminUrl"
        :name="name"
        :orcid="orcid"
        :is-staff="isStaff"
    ></UserMenuOffcanvas>
</template>