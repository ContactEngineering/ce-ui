<script setup lang="ts">

import { QBtn, QIcon } from "quasar";
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
              :href="lastTab.href_previous"
              icon="chevron_left" />
            <QBtn
                v-for="(tab, index) in tabs" :key="index"
                :flat="!tab.active"
                dense
                no-caps
                :color="tab.active ? 'dark' : 'white'"
                :href="tab.href"
                :icon="tab.icon"
                :label="tab.title"
            />
            <QBtn v-if="lastTab?.href_next"
              flat round dense
              :href="lastTab.href_next"
              icon="chevron_right" />
    </div>
</template>
