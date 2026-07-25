<script setup lang="ts">

import {computed} from "vue";
import {BBadge} from "bootstrap-vue-next";

const props = defineProps({
    status: {type: String, required: true},
    acceptedOn: {type: String, default: null}
});

// Keep in sync with the TERMS_* constants in
// topobank_rest_api/staff/queries.py.
const presentation = {
    accepted: {variant: "success", label: "Accepted"},
    partial: {variant: "warning", label: "Partial"},
    not_accepted: {variant: "danger", label: "Not accepted"},
    exempt: {variant: "info", label: "Exempt"},
    not_required: {variant: "secondary", label: "None active"},
    unavailable: {variant: "secondary", label: "Unknown"}
};

const badge = computed(() => presentation[props.status]
    ?? {variant: "secondary", label: props.status});

const title = computed(() => {
    if (props.status === "exempt") {
        return "This user holds the permission to skip the terms of use";
    }
    if (props.acceptedOn != null) {
        return `Last accepted ${new Date(props.acceptedOn).toLocaleString()}`;
    }
    return "Never accepted the currently active terms of use";
});

</script>

<template>
    <BBadge :variant="badge.variant" :title="title">{{ badge.label }}</BBadge>
</template>
