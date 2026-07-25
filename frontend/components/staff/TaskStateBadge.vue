<script setup lang="ts">

import {computed} from "vue";
import {BBadge} from "bootstrap-vue-next";

const props = defineProps({
    state: {type: String, required: true},
    label: {type: String, default: null}
});

// Task state codes as defined by TaskStateModel in topobank/taskapp/models.py.
const presentation = {
    st: {variant: "primary", label: "Running"},
    pe: {variant: "warning", label: "Pending"},
    pd: {variant: "warning", label: "Waiting for dependencies"},
    re: {variant: "warning", label: "Retrying"},
    su: {variant: "success", label: "Success"},
    fa: {variant: "danger", label: "Failure"},
    no: {variant: "secondary", label: "Not run"}
};

const badge = computed(() => presentation[props.state]
    ?? {variant: "secondary", label: props.label ?? props.state});

</script>

<template>
    <BBadge :variant="badge.variant">
        <i v-if="state === 'st'" class="fa fa-circle-notch fa-spin me-1"></i>
        {{ badge.label }}
    </BBadge>
</template>
