<script setup>

import {computed} from "vue";

import {formatExponential} from "@/utils/formatting";
import {paperSection} from "@/utils/references";
import HelpTooltip from "@/components/ui/HelpTooltip.vue";

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
</script>

<template>
    <div v-if="topography !== null && topography.resolution_y !== null">
        <span class="badge bg-warning ms-1">{{ topography.datafile_format }}</span>
        <span class="badge bg-info ms-2">{{ topography.resolution_x }} &times; {{
                topography.resolution_y
            }} data points</span>
        <span v-if="topography.has_undefined_data" class="badge bg-danger ms-2">undefined data
            <HelpTooltip label="About undefined data"
                text="Some pixels have no measured value (data gaps). You can choose how to handle these under the Filters tab (leave undefined, or fill by harmonic interpolation)."/>
        </span>
        <span v-if="isMetadataIncomplete" class="badge bg-danger ms-2">metadata incomplete
            <HelpTooltip label="About incomplete metadata"
                text="Required metadata (physical size, unit and height scale) is missing, so this measurement cannot be analyzed yet. Edit the metadata to complete it."/>
        </span>
        <span v-if="topography.short_reliability_cutoff !== null" class="badge bg-dark ms-2">
                    reliability cutoff {{ shortReliabilityCutoff }}
            <HelpTooltip label="About the reliability cutoff"
                text="Smallest length scale that can be trusted for this measurement. Below it, features are distorted by the tip radius or instrument resolution and are excluded from analyses."
                :link-url="paperSection('as4-9')"
                link-text="Reliability analysis (§4.9)"/>
                </span>
    </div>
    <div v-if="topography !== null && topography.resolution_y === null">
        <div class="badge bg-warning ms-1">{{ topography.datafile_format }}</div>
        <div class="badge bg-info ms-2">{{ topography.resolution_x }} data points</div>
        <span v-if="topography.has_undefined_data" class="badge bg-danger ms-2">undefined data
            <HelpTooltip label="About undefined data"
                text="Some pixels have no measured value (data gaps). You can choose how to handle these under the Filters tab (leave undefined, or fill by harmonic interpolation)."/>
        </span>
        <span v-if="isMetadataIncomplete" class="badge bg-danger ms-2">metadata incomplete
            <HelpTooltip label="About incomplete metadata"
                text="Required metadata (physical size, unit and height scale) is missing, so this measurement cannot be analyzed yet. Edit the metadata to complete it."/>
        </span>
        <span v-if="topography.short_reliability_cutoff !== null" class="badge bg-dark ms-2">
                    reliability cutoff {{ shortReliabilityCutoff }}
            <HelpTooltip label="About the reliability cutoff"
                text="Smallest length scale that can be trusted for this measurement. Below it, features are distorted by the tip radius or instrument resolution and are excluded from analyses."
                :link-url="paperSection('as4-9')"
                link-text="Reliability analysis (§4.9)"/>
                </span>
    </div>
</template>
