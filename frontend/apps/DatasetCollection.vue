<script setup lang="ts">

import axios from "axios";
import { inject, ref } from "vue";

const appProps = inject("appProps");

const collection = ref({});
const publications = ref([]);
const datasets = ref([]);

function datetimeToDateString(timestamp) {
    const date = new Date(timestamp);
    return date.toISOString().substring(0, 10);
}

axios.get(appProps.object.url).then((response) => {
    collection.value = response.data;
    response.data.publications.forEach((publication_url) => {
        axios.get(publication_url).then((response) => {
            publications.value.push(response.data);
            axios.get(response.data.surface).then((response) => {
                datasets.value.push(response.data);
            });
        })
    })

}).catch((err) => {
    console.error(err);
});

</script>
<template>
    <div class="container">
        <h1>
            {{ collection.title }}
        </h1>
        <p style="white-space: pre-wrap;">
            {{ collection.description }}
        </p>
        <h2>Publications</h2>
        <div class="d-flex flex-row mb-5">
            <div v-for="(dataset, index) in datasets" :key="dataset.id">
                <a :href="`/ui/dataset-detail/${dataset.id}/`"
                    class="publication-card border rounded ms-2 p-2 d-flex flex-column">
                    <span class=" dataset-title">
                        <i class="fa fa-layer-group"></i> {{ dataset.name }}
                    </span>
                    <span>Published by: {{ publications[index].publisher.name }}</span>
                    <span>Publish date: {{ datetimeToDateString(publications[index].datetime) }}</span>
                </a>
            </div>
        </div>
    </div>
</template>

<style scoped>
.dataset-title {
    font-size: medium;
    font-weight: bold;
}

.publication-card {
    all: unset;
    color: inherit;
    text-decoration: none;

    &:hover {
        color: #007BFF;
        cursor: pointer;
    }
}
</style>
