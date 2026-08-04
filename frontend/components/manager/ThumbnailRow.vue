<script setup lang="ts">

import {computed, ref} from "vue";

import {BButton} from "bootstrap-vue-next";

import Thumbnail from "@/components/manager/Thumbnail.vue";

/* The dataset list response already contains every measurement of every
   dataset (`topography_set`), so the thumbnails are rendered from that data
   instead of each row fetching its measurements again from the API. */
const props = defineProps({
    dataSources: {
        type: Array,
        default: () => []
    },
    nbThumbnailsIncrement: {
        type: Number,
        default: 5
    }
});

const _nbVisible = ref<number>(props.nbThumbnailsIncrement);

const visibleDataSources = computed(() => {
    return props.dataSources.slice(0, _nbVisible.value);
});

</script>

<template>
    <div class="thumbnail-row">
        <Thumbnail v-for="dataSource in visibleDataSources"
                   :key="dataSource.id"
                   class="me-1"
                   img-class="mh-100"
                   :data-source="dataSource">
        </Thumbnail>
        <BButton v-if="dataSources.length > _nbVisible"
                 variant="light" size="sm" class="me-1"
                 @click="_nbVisible += nbThumbnailsIncrement">
            <i class="fa fa-ellipsis align-self-center"></i>
        </BButton>
    </div>
</template>

<style scoped>

.thumbnail-row {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    height: 2rem;
    overflow: hidden;
}

.thumbnail-row :deep(img) {
    height: 2rem;
    width: 2rem;
    object-fit: cover;
}

</style>
