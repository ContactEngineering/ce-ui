<script setup lang="ts">

import { QBtn } from 'quasar';

import { subjectsToBase64 } from "../utils/api";

const props = defineProps({
    detailUrl: String,
    functionName: String,
    subjects: Object
});

</script>

<template>
    <QBtn flat size="sm" :href="`${detailUrl}${functionName}/?subjects=${subjectsToBase64(subjects)}`">
        <i class="fa fa-expand"></i>
    </QBtn>
</template>
