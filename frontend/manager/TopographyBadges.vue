<script setup>

import { computed } from "vue";
import { QChip, QIcon } from "quasar";

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

const dimensionText = computed(() => {
    if (props.topography.resolution_y !== null) {
        return '2D';
    }
    return '1D';
});
</script>

<template>
    <div v-if="topography !== null" class="row items-center q-gutter-xs">
        <QChip dense size="sm" color="grey-3" text-color="grey-8" icon="insert_drive_file">
            {{ topography.datafile_format }}
        </QChip>
        <QChip dense size="sm" color="grey-3" text-color="grey-8" icon="grid_on">
            {{ resolutionText }}
        </QChip>
        <QChip dense size="sm" color="grey-3" text-color="grey-8" icon="straighten">
            {{ dimensionText }}
        </QChip>
        <QChip v-if="topography.has_undefined_data"
               dense size="sm" color="orange-2" text-color="orange-9" icon="warning">
            undefined data
        </QChip>
        <QChip v-if="isMetadataIncomplete"
               dense size="sm" color="orange-2" text-color="orange-9" icon="edit_note">
            metadata incomplete
        </QChip>
        <QChip v-if="topography.short_reliability_cutoff !== null"
               dense size="sm" color="blue-grey-2" text-color="blue-grey-8" icon="content_cut">
            cutoff {{ shortReliabilityCutoff }}
        </QChip>
    </div>
</template>
