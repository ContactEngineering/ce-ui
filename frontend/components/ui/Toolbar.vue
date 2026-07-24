<script setup lang="ts">
/**
 * A framed toolbar row (a compact card) that hosts page/tab actions such as
 * "Select all", "Edit" or "Save / Discard". Using it everywhere keeps all
 * toolbars visually identical across the app.
 */

import { BCard } from "bootstrap-vue-next";

defineProps({
    // Horizontal alignment of the toolbar contents, mapped to a Bootstrap
    // `justify-content-*` utility (e.g. "end", "between", "start", "center").
    justify: { type: String, default: "end" },
    // When true (default) the toolbar is wrapped in its own card frame. Set to
    // false to render just the action row (e.g. inside an existing card).
    framed: { type: Boolean, default: true }
});
</script>

<template>
    <BCard v-if="framed" body-class="py-2" class="mb-1">
        <div class="d-flex align-items-center flex-wrap gap-2"
             :class="`justify-content-${justify}`">
            <slot></slot>
        </div>
    </BCard>
    <div v-else class="d-flex align-items-center flex-wrap gap-2 py-2"
         :class="`justify-content-${justify}`">
        <slot></slot>
    </div>
</template>
