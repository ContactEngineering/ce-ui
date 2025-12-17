<script setup>

import { computed, ref } from "vue";

import { QInnerLoading, QSpinner, QIcon } from "quasar";

const props = defineProps({
    dataSource: Object,
    size: {
        type: String,
        default: '64px'
    }
});

const _isLoading = ref(true);

const hasThumbnail = computed(() => {
    return props.dataSource.thumbnail != null && props.dataSource.thumbnail.file != null;
});

</script>

<template>
    <div class="thumbnail-wrapper" :style="{ width: size, height: size }">
        <a :href="`/ui/topography/${dataSource.id}/`">
            <img v-if="hasThumbnail"
                 class="thumbnail-img"
                 :src="dataSource.thumbnail.file"
                 @load="_isLoading = false">
            <div v-if="!hasThumbnail" class="thumbnail-placeholder">
                <QIcon name="insert_chart" size="32px" color="grey-6" />
            </div>
        </a>
        <QInnerLoading :showing="hasThumbnail && _isLoading">
            <QSpinner size="1rem" />
        </QInnerLoading>
    </div>
</template>

<style scoped>
.thumbnail-wrapper {
    position: relative;
    flex-shrink: 0;
    border-radius: 4px;
    overflow: hidden;
    background: #f5f5f5;
}

.thumbnail-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.thumbnail-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
}
</style>