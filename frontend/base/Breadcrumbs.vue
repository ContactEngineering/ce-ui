<script setup lang="ts">

import { QBreadcrumbs, QBreadcrumbsEl, QBtn, QIcon } from "quasar";
import { computed } from "vue";

interface Tab {
    title: string;
    icon?: string;
    href: string;
    href_previous?: string;
    href_next?: string;
    active?: boolean;
    tooltip?: string;
}

const props = defineProps<{
    tabs: Tab[]
}>();

// Get the last tab for prev/next navigation
const lastTab = computed(() => props.tabs?.[props.tabs.length - 1]);

</script>

<template>
    <div v-if="tabs && tabs.length > 0" class="row items-center no-wrap">
        <QBtn v-if="lastTab?.href_previous"
              flat round dense
              color="white"
              :href="lastTab.href_previous"
              icon="chevron_left"
              class="q-mr-sm" />
        <QBreadcrumbs active-color="white" separator-color="grey-5" class="text-grey-4">
            <QBreadcrumbsEl v-for="(tab, index) in tabs"
                            :key="index"
                            :label="tab.title"
                            :icon="tab.icon"
                            :href="tab.href"
                            :class="{ 'text-white text-weight-medium': tab.active }" />
        </QBreadcrumbs>
        <QBtn v-if="lastTab?.href_next"
              flat round dense
              color="white"
              :href="lastTab.href_next"
              icon="chevron_right"
              class="q-ml-sm" />
    </div>
</template>
