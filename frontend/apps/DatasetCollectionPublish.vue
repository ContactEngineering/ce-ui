<script setup lang="ts">

import axios from "axios";
import { inject, ref } from "vue";

import { BButton } from 'bootstrap-vue-next';

const appProps = inject("appProps");
const datasets = ref([]);
const publications = ref([]);

appProps.searchParams.getAll("dataset").forEach(datasetId => {
    axios.get("/manager/api/surface/" + datasetId).then((datasetResponse) => {
        axios.get(datasetResponse.data.publication).then((publicationResponse) => {
            publications.value.push(publicationResponse.data);
            datasets.value.push(datasetResponse.data);
        }).catch((err) => {
            console.error("An error occured while getting the publication:\n", err);
        });
    }).catch((err) => {
        console.error("An error occured while getting the dataset:\n", err);
    });
});

function datetimeToDateString(timestamp) {
    const date = new Date(timestamp);
    return date.toISOString().substring(0, 10);
}

function publish() {
    axios.post('/go/publish-collection/', {
        publication: publications.value.map(publication => publication.id)
    }).then((response) => {
        console.log(response);
    });

}

</script>
<template>
    <div class="container">
        <h1>Publish a collection</h1>
        <div class="d-flex flex-row">
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

        <div class="d-flex flex-row justify-content-end">
            <BButton @click="publish()" variant="success" size="lg">
                Publish 🚀
            </BButton>
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
