<script setup>

import axios from "axios";
import {onMounted, ref} from "vue";

import {BOverlay} from "bootstrap-vue-next";

import Thumbnail from "./Thumbnail.vue";

const props = defineProps({
    dataSourceListUrl: String,
    maxNbThumbnails: {
        type: Number,
        default: 20
    }
});

const _dataSources = ref([]);
const _nbDataSources = ref(0);
const _isLoading = ref(true);

onMounted(() => {
    _isLoading.value = true;
    axios.get(`${props.dataSourceListUrl}&limit=${props.maxNbThumbnails}`)
        .then(response => {
            _dataSources.value = response.data.results;
            _nbDataSources.value = response.data.count;
        })
        .finally(() => {
            _isLoading.value = false;
        });
});

</script>

<template>
    <BOverlay class="thumbnail-row" :show="_isLoading">
        <Thumbnail v-for="dataSource in _dataSources"
                   :key="dataSource.id"
                   class="me-1"
                   img-class="mh-100"
                   :data-source="dataSource">
        </Thumbnail>
        <i v-if="_nbDataSources > _dataSources.length"
           class="fa fa-ellipsis align-self-center"></i>
    </BOverlay>
</template>

<style scoped>

.thumbnail-row {
    display: flex;
    height: 2rem;
}

</style>