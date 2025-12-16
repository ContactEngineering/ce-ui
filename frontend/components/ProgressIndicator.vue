<script setup>

import { QBtn, QSpinner } from "quasar";

const props = defineProps({
    value: {type: Number, default: 0},
    max: {type: Number, default: 100},
    state: {type: String, default: null}
});

</script>

<template>
    <QBtn v-if="state === 'su'" color="positive" disable flat>
        <i class="fa fa-check text-white"></i>
    </QBtn>
    <QBtn v-if="state === 'fa'" color="negative" disable flat>
        <i class="fa fa-circle text-white"></i>
    </QBtn>
    <QBtn v-if="state === 'pe'" color="grey-3" disable flat>
        <QSpinner size="sm" />
    </QBtn>
    <QBtn v-if="!['su', 'fa', 'pe'].includes(state)" color="grey-3" disable flat>
        {{ Math.round(value * 100 / max) }} %
    </QBtn>
</template>
