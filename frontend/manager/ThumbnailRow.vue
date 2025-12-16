<script setup lang="ts">

import axios from "axios";
import {onMounted, ref} from "vue";

import {BButton, BOverlay} from "bootstrap-vue-next";

import Thumbnail from "./Thumbnail.vue";

const props = defineProps({
    dataSourceListUrl: String,
    nbThumbnailsIncrement: {
        type: Number,
        default: 5
    }
});

const _dataSources = ref([]);
const _nbDataSources = ref<number>(0);
const _nbThumbnails = ref<number>(0);
const _isLoading = ref<boolean>(true);

onMounted(() => {
    loadMoreThumbnails();
});

function loadMoreThumbnails() {
    _isLoading.value = true;
    axios.get(`${props.dataSourceListUrl}&offset=${_nbThumbnails.value}&limit=${_nbThumbnails.value + props.nbThumbnailsIncrement}`)
        .then(response => {
            _dataSources.value.push(...response.data.results);
            _nbDataSources.value = response.data.count;
            _nbThumbnails.value += props.nbThumbnailsIncrement;
        })
        .finally(() => {
            _isLoading.value = false;
        });
}

</script>

<template>
    <BOverlay class="thumbnail-row" :show="_isLoading">
        <Thumbnail v-for="dataSource in _dataSources"
                   :key="dataSource.id"
                   class="me-1"
                   img-class="mh-100"
                   :data-source="dataSource">
        </Thumbnail>
        <BButton v-if="_nbDataSources > _dataSources.length"
                 variant="light" size="sm" class="me-1"
                 @click="loadMoreThumbnails">
            <i class="fa fa-ellipsis align-self-center"></i>
        </BButton>
    </BOverlay>
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