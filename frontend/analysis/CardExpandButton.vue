<script setup>

import {BButton} from 'bootstrap-vue-next';

import {subjectsToBase64} from "../utils/api";

const props = defineProps({
    detailUrl: String,
    functionId: Number,
    subjects: Object
});

</script>

<template>
    <BButton variant="outline-secondary"
             size="sm">
        <a :href="`${detailUrl}${functionId}/?subjects=${subjectsToBase64(subjects)}`"
           class="text-reset">
            <i class="fa fa-expand"></i>
        </a>
    </BButton>
</template>
