<script setup>

import {BButton, BSpinner} from "bootstrap-vue-next";

const props = defineProps({
    value: {type: Number, default: 0},
    max: {type: Number, default: 100},
    state: {type: String, default: null}
});

</script>

<template>
    <BButton v-if="state === 'su'" variant="success" disabled>
        <i class="fa fa-check text-white"></i>
    </BButton>
    <BButton v-if="state === 'fa'" variant="danger" disabled>
        <i class="fa fa-circle text-white"></i>
    </BButton>
    <BButton v-if="state === 'pe'" variant="light" disabled>
        <BSpinner small type="grow"></BSpinner>
    </BButton>
    <BButton v-if="!['su', 'fa', 'pe'].includes(state)" variant="light" disabled>
        {{ Math.round(value * 100 / max) }} %
    </BButton>
</template>
