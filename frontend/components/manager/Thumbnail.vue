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

/* The v2 measurement summary carries a flat `thumbnail_url`; the full v1
   topography representation nests it as `thumbnail.file`. */
const thumbnailUrl = computed(() => {
    return props.dataSource.thumbnail_url ?? props.dataSource.thumbnail?.file ?? null;
});

const hasThumbnail = computed(() => {
    return thumbnailUrl.value != null;
});

</script>

<template>
    <BOverlay :show="hasThumbnail && !hasFailed && _isLoading">
        <a :href="`/ui/topography/${dataSource.id}/`"
           :title="hasFailed ? 'Processing of this measurement failed' : dataSource.name">
            <i v-if="hasFailed"
               :class="`fa-solid fa-triangle-exclamation fa-2x text-danger ${imgClass}`"></i>
            <!-- Lazy loading keeps off-screen rows from competing with the
                 visible ones for the browser's connection budget -->
            <img v-else-if="hasThumbnail"
                 :class="imgClass"
                 :src="thumbnailUrl"
                 :alt="dataSource.name"
                 loading="lazy"
                 decoding="async"
                 @load="_isLoading = false"
                 @error="_isLoading = false">
            <i v-else
               :class="`fa fa-microscope fa-2x text-black ${imgClass}`"></i>
        </a>
    </BOverlay>
</template>