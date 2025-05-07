<script setup lang="ts">

import axios from "axios";
import { inject, ref, computed } from "vue";

import {
    BButton,
    BAlert,
    BFormInput,
    BFormTextarea,
    BSpinner,
    useToastController
} from 'bootstrap-vue-next';


const appProps = inject("appProps");
const datasets = ref([]);
const publications = ref([]);
const title = ref("");
const validTitle = ref(null);
const description = ref("");
const pending_request = ref(false);
const { show } = useToastController();

const datasetIds = appProps.searchParams.getAll("dataset");
const invalid_id = ref(false);

datasetIds.forEach(datasetId => {
    axios.get("/manager/api/surface/" + datasetId).then((datasetResponse) => {
        axios.get(datasetResponse.data.publication).then((publicationResponse) => {
            publications.value.push(publicationResponse.data);
            datasets.value.push(datasetResponse.data);
        }).catch((err) => {
            console.error("An error occured while getting the publication:\n", err);
            invalid_id.value = true;
            show?.({
                props: {
                    title: "Dataset not published",
                    body: `For the dataset with ID:${datasetId} is not published.`,
                    variant: 'danger'
                }
            });
        });
    }).catch((err) => {
        console.error("An error occured while getting the dataset:\n", err);

        invalid_id.value = true;
        show?.({
            props: {
                title: "Could not find datasets",
                body: `The dataset with ID:${datasetId} could not be found.`,
                variant: 'danger'
            }
        });
    });
});

function datetimeToDateString(timestamp) {
    const date = new Date(timestamp);
    return date.toISOString().substring(0, 10);
}

function publish() {
    validTitle.value = title.value != "";
    if (validTitle.value) {
        pending_request.value = true;
        axios.post('/go/publish-collection/', {
            publication: publications.value.map(publication => publication.id),
            title: title.value,
            description: description.value
        }).then((response) => {
            window.location.href = `/ui/dataset-collection/${response.data.collection_id}/`;
        }).catch((err) => {
            console.error(err);
            pending_request.value = false;
        });
    }
}

const validSelection = computed(() => {
    return datasetIds.length > 1 && !invalid_id.value
});

</script>
<template>
    <div class="container">
        <h1>Publish a collection</h1>
        <div v-if="validSelection">

            <BAlert :model-value="true" variant="info">
                <h4 class="alert-heading">You are about to create a publication collection</h4>
                <p>
                    A publication collection is a object that bundles already published datasets. <br>
                    The Colection will be published under the <a
                        href="https://creativecommons.org/publicdomain/zero/1.0/">
                        CC0 1.0 Universal </a> license. <br>
                    You will be the author of the collection.
                </p>
                <hr />
                <p class="mb-0">
                    Do you understand this and want to continue?
                </p>
            </BAlert>
            <h3>Title*</h3>
            <BFormInput id="collection-title" v-model="title" :state="validTitle"
                placeholder="Enter the collection title" />
            <h3 class="mt-2">Description</h3>
            <BFormTextarea v-model="description" placeholder="Enter a description..." rows="3" />
            <h3 class="mt-2">Publications:</h3>
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
            <div class="d-flex flex-row justify-content-end">
                <BButton v-if="pending_request" disabled variant="success" size="lg">
                    Publish
                    <BSpinner variant="primary" style="width: 1.2rem; height: 1.2rem;" />
                </BButton>
                <BButton v-else @click="publish()" variant="success" size="lg">
                    Publish 🚀
                </BButton>
            </div>
        </div>
        <BAlert v-else :model-value="true" variant="danger">
            <h4 class="alert-heading">This will not work!</h4>
            <p>
                A publication collection, bundles 2 or more published datasets. <br>
            </p>
            <hr />
            <p class="mb-0">
                Your selection does not meet that requirement.
            </p>
        </BAlert>
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
