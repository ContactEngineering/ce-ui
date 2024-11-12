<script setup>

import {BOffcanvas} from "bootstrap-vue-next";

const visible = defineModel("visible");

const props = defineProps({
    name: String,
    apiUrl: String
});

</script>

<template>
    <BOffcanvas v-model="visible" placement="end">
        <h3>{{ name }}</h3>
    </BOffcanvas>
</template>