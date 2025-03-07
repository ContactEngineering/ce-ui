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

const hasThumbnail = computed(() => {
    return props.dataSource.thumbnail != null && props.dataSource.thumbnail.file != null;
});

</script>

<template>
    <BOverlay :show="hasThumbnail && _isLoading">
        <a :href="`/ui/topography/${dataSource.id}/`">
            <img v-if="hasThumbnail"
                 :class="imgClass"
                 :src="dataSource.thumbnail.file"
                 @load="_isLoading = false">
            <i v-if="!hasThumbnail"
               :class="`fa fa-microscope fa-2x text-black ${imgClass}`"></i>
        </a>
    </BOverlay>
</template>