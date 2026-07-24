<script setup lang="ts">
/**
 * Small inline help affordance: an info icon that reveals a popover with a
 * short explanation and an optional "learn more" link (e.g. to a section of
 * the reference paper). Use this for jargon or fields that need more than a
 * one-word label.
 */

import { BPopover } from "bootstrap-vue-next";

defineProps({
    // Explanatory text shown in the popover body.
    text: { type: String, default: "" },
    // Optional bold heading for the popover.
    title: { type: String, default: null },
    // Optional URL rendered as a link at the bottom of the popover.
    linkUrl: { type: String, default: null },
    // Label for the optional link.
    linkText: { type: String, default: "Learn more" },
    // Popover placement relative to the icon.
    placement: { type: String, default: "top" },
    // Accessible label for the trigger.
    label: { type: String, default: "More information" }
});
</script>

<template>
    <BPopover :placement="placement" :title="title" hover focus>
        <template #target>
            <span class="help-tooltip text-secondary"
                  role="button"
                  tabindex="0"
                  :aria-label="label">
                <i class="fa-solid fa-circle-info"></i>
            </span>
        </template>
        <div v-if="text">{{ text }}</div>
        <slot></slot>
        <a v-if="linkUrl"
           :href="linkUrl"
           target="_blank"
           rel="noopener"
           class="d-inline-block mt-2">
            {{ linkText }}
            <i class="fa-solid fa-arrow-up-right-from-square ms-1 small"></i>
        </a>
    </BPopover>
</template>

<style scoped>
.help-tooltip {
    cursor: help;
}
</style>
