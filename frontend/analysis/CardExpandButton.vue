<script setup>

import {BButton} from 'bootstrap-vue-next';

const props = defineProps({
    detailUrl: String,
    functionId: Number,
    subjects: String
});

</script>

<template>
    <BButton variant="outline-secondary"
             size="sm">
        <a :href="`${detailUrl}${functionId}/?subjects=${subjects}`"
           class="text-reset">
            <i class="fa fa-expand"></i>
        </a>
    </BButton>
</template>
