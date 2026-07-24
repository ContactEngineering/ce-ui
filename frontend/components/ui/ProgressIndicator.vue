<script setup>

import {computed} from "vue";

import {BProgress} from "bootstrap-vue-next";

const props = defineProps({
    value: {type: Number, default: 0},
    max: {type: Number, default: 100},
    state: {type: String, default: null}
});

const percent = computed(() => {
    if (props.max === 0) {
        return 0;
    }
    return Math.round((props.value * 100) / props.max);
});

// Map the task state to a standard Bootstrap progress bar: a solid green/red
// bar for the terminal states, and a striped, animated bar while pending or
// running.
const bar = computed(() => {
    switch (props.state) {
        case "su":
            return {value: 100, variant: "success", label: "Done", striped: false, animated: false};
        case "fa":
            return {value: 100, variant: "danger", label: "Failed", striped: false, animated: false};
        case "st":
            return {value: percent.value, variant: "primary", label: `${percent.value}%`, striped: true, animated: true};
        case "pe":
            return {value: 100, variant: "info", label: "Pending", striped: true, animated: true};
        default:
            // Not run yet / unknown state
            return {value: percent.value, variant: "secondary", label: `${percent.value}%`, striped: true, animated: true};
    }
});

</script>

<template>
    <BProgress :value="bar.value"
               :max="100"
               :variant="bar.variant"
               :striped="bar.striped"
               :animated="bar.animated"
               :label="bar.label"
               height="1.5rem"/>
</template>
