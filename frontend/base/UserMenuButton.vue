<script setup>

import { inject } from "vue";
import { QBtn } from "quasar";

const props = defineProps({
    name: String
});

const rightDrawer = inject('rightDrawer');

function openUserMenu() {
    rightDrawer.open('user');
}

</script>

<template>
    <QBtn flat @click="openUserMenu" icon="account_circle">
        <span class="q-ml-xs gt-xs">{{ name }}</span>
    </QBtn>
</template>
