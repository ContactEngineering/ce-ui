<script setup lang="ts">

import {BButton} from 'bootstrap-vue-next';

import {subjectsToBase64} from "@/utils/api";

const props = defineProps({
    detailUrl: String,
    functionName: String,
    subjects: Object
});

</script>

<template>
    <BButton variant="primary"
             size="sm">
        <a :href="`${detailUrl}${functionName}/?subjects=${subjectsToBase64(subjects)}`"
           class="text-reset">
            <i class="fa fa-expand"></i>
        </a>
    </BButton>
</template>
