<script setup>

import {computed, ref} from "vue";

import {BOverlay} from "bootstrap-vue-next";

const props = defineProps({
    dataSource: Object,
    imgClass: {
        type: String,
        default: ''
    }
});

const _isLoading = ref(true);

// Processing of the measurement failed: show a red placeholder instead of
// spinning forever waiting for a thumbnail that will never arrive.
const hasFailed = computed(() => {
    return props.dataSource.task_state === 'fa';
});

const hasThumbnail = computed(() => {
    return props.dataSource.thumbnail != null && props.dataSource.thumbnail.file != null;
});

</script>

<template>
    <BOverlay :show="hasThumbnail && !hasFailed && _isLoading">
        <a :href="`/ui/topography/${dataSource.id}/`"
           :title="hasFailed ? 'Processing of this measurement failed' : dataSource.name">
            <i v-if="hasFailed"
               :class="`fa-solid fa-triangle-exclamation fa-2x text-danger ${imgClass}`"></i>
            <img v-else-if="hasThumbnail"
                 :class="imgClass"
                 :src="dataSource.thumbnail.file"
                 @load="_isLoading = false"
                 @error="_isLoading = false">
            <i v-else
               :class="`fa fa-microscope fa-2x text-black ${imgClass}`"></i>
        </a>
    </BOverlay>
</template>