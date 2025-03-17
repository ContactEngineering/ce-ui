<script setup lang="ts">

import axios from "axios";
import {onMounted, ref} from "vue";

import {BButton, BOverlay} from "bootstrap-vue-next";

import Thumbnail from "./Thumbnail.vue";

const props = defineProps({
    dataSourceListUrl: String,
    nbThumbnailsIncrement: {
        type: Number,
        default: 20
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
    _nbThumbnails.value += props.nbThumbnailsIncrement;
    axios.get(`${props.dataSourceListUrl}&limit=${_nbThumbnails.value}`)
        .then(response => {
            _dataSources.value = response.data?.results;
            _nbDataSources.value = response.data?.count;
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
    height: 2rem;
}

</style>