<script setup lang="ts">
/**
 * Centered spinner with a message, shown while data is being fetched.
 */

import {BSpinner} from "bootstrap-vue-next";

defineProps({
    message: {
        type: String,
        default: "Loading..."
    }
});
</script>

<template>
    <div class="d-flex justify-content-center mt-5">
        <div class="flex-column text-center">
            <BSpinner/>
            <p>{{ message }}</p>
        </div>
    </div>
</template>
