<script setup>

import { computed } from "vue";
import { QBadge } from "quasar";

import { formatExponential } from "topobank/utils/formatting";

const props = defineProps({
    topography: Object
});

const isMetadataIncomplete = computed(() => {
    if (props.topography !== null && props.topography.is_metadata_complete !== undefined) {
        return !props.topography.is_metadata_complete;
    } else {
        return true;
    }
});

const shortReliabilityCutoff = computed(() => {
    return formatExponential(props.topography.short_reliability_cutoff, 2) + ` m`;
});

const resolutionText = computed(() => {
    if (props.topography.resolution_y !== null) {
        return `${props.topography.resolution_x} × ${props.topography.resolution_y} pts`;
    }
    return `${props.topography.resolution_x} pts`;
});
</script>

<template>
    <div v-if="topography !== null" class="row items-center q-gutter-xs">
        <QBadge color="warning" text-color="dark">{{ topography.datafile_format }}</QBadge>
        <QBadge color="info">{{ resolutionText }}</QBadge>
        <QBadge v-if="topography.has_undefined_data" color="negative">undefined data</QBadge>
        <QBadge v-if="isMetadataIncomplete" color="negative">metadata incomplete</QBadge>
        <QBadge v-if="topography.short_reliability_cutoff !== null" color="grey-8">
            cutoff {{ shortReliabilityCutoff }}
        </QBadge>
    </div>
</template>
