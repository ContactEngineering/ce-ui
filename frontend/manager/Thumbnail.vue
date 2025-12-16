<script setup>

import {computed, ref} from "vue";

import { QInnerLoading, QSpinner } from "quasar";

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
    <div class="thumbnail-wrapper">
        <a :href="`/ui/topography/${dataSource.id}/`">
            <img v-if="hasThumbnail"
                 :class="imgClass"
                 :src="dataSource.thumbnail.file"
                 @load="_isLoading = false">
            <i v-if="!hasThumbnail"
               :class="`fa fa-microscope fa-2x text-black ${imgClass}`"></i>
        </a>
        <QInnerLoading :showing="hasThumbnail && _isLoading">
            <QSpinner size="1rem" />
        </QInnerLoading>
    </div>
</template>

<style scoped>
.thumbnail-wrapper {
    position: relative;
    display: inline-block;
}
</style>