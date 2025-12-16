<script setup lang="ts">

import { inject, ref, computed } from "vue";

import {
    QBtn,
    QBanner,
    QInput,
    QSpinner
} from 'quasar';

import { useNotify } from "@/utils/notify";
import {
    managerApiSurfaceRetrieve,
    goPublicationRetrieve,
    goPublishCollectionCreate
} from "@/api";
import { getIdFromUrl } from "@/utils/api";


const appProps = inject("appProps");
const datasets = ref([]);
const publications = ref([]);
const title = ref("");
const validTitle = ref(null);
const description = ref("");
const pending_request = ref(false);
const { show } = useNotify();

const datasetIds = appProps.searchParams.getAll("dataset");
const invalid_id = ref(false);

async function loadDatasets() {
    for (const datasetId of datasetIds) {
        try {
            const datasetResponse = await managerApiSurfaceRetrieve({path: {id: parseInt(datasetId)}});
            const publicationId = getIdFromUrl(datasetResponse.data.publication);
            const publicationResponse = await goPublicationRetrieve({path: {id: publicationId}});
            publications.value.push(publicationResponse.data);
            datasets.value.push(datasetResponse.data);
        } catch (err) {
            console.error("An error occurred while getting the dataset or publication:\n", err);
            invalid_id.value = true;
            show?.({
                props: {
                    title: "Could not load dataset",
                    body: `The dataset with ID:${datasetId} could not be found or is not published.`,
                    variant: 'danger'
                }
            });
        }
    }
}

loadDatasets();

function datetimeToDateString(timestamp) {
    const date = new Date(timestamp);
    return date.toISOString().substring(0, 10);
}

async function publish() {
    validTitle.value = title.value != "";
    if (validTitle.value) {
        pending_request.value = true;
        try {
            const response = await goPublishCollectionCreate({
                body: {
                    publication: publications.value.map(publication => publication.id),
                    title: title.value,
                    description: description.value
                } as any
            });
            window.location.href = `/ui/dataset-collection/${response.data.collection_id}/`;
        } catch (err: any) {
            console.error(err.response?.statusText);
            pending_request.value = false;
            show?.({
                props: {
                    title: "Publishing failed",
                    body: err.response?.statusText,
                    variant: 'danger'
                }
            });
        }
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
            <QBanner class="bg-info text-white q-mb-md">
                <template v-slot:avatar>
                    <q-icon name="info" />
                </template>
                <h4>You are about to create a publication collection</h4>
                <p>
                    A publication collection is a object that bundles already published datasets. <br>
                    The Collection will be published under the <a
                        href="https://creativecommons.org/publicdomain/zero/1.0/"
                        class="text-white text-underline">
                        CC0 1.0 Universal </a> license. <br>
                    You will be the author of the collection.
                </p>
                <hr class="bg-white" />
                <p class="q-ma-none">
                    Do you understand this and want to continue?
                </p>
            </QBanner>
            <h3>Title*</h3>
            <QInput v-model="title"
                    :error="validTitle === false"
                    error-message="Title is required"
                    placeholder="Enter the collection title"
                    outlined />
            <h3 class="q-mt-md">Description</h3>
            <QInput v-model="description"
                    type="textarea"
                    placeholder="Enter a description..."
                    rows="3"
                    outlined />
            <h3 class="q-mt-md">Publications:</h3>
            <div class="flex row q-gutter-md q-mb-xl">
                <div v-for="(dataset, index) in datasets" :key="dataset.id">
                    <a :href="`/ui/dataset-detail/${dataset.id}/`" class="publication-card">
                        <span class="dataset-title">
                            <q-icon name="layers" /> {{ dataset.name }}
                        </span>
                        <span>Published by: {{ publications[index].publisher.name }}</span>
                        <span>Publish date: {{ datetimeToDateString(publications[index].datetime) }}</span>
                    </a>
                </div>
            </div>
            <div class="flex justify-end">
                <QBtn v-if="pending_request" disable color="positive" size="lg">
                    Publish
                    <QSpinner color="white" size="1.2rem" class="q-ml-sm" />
                </QBtn>
                <QBtn v-else @click="publish()" color="positive" size="lg">
                    Publish 🚀
                </QBtn>
            </div>
        </div>
        <QBanner v-else class="bg-negative text-white">
            <template v-slot:avatar>
                <q-icon name="warning" />
            </template>
            <h4>This will not work!</h4>
            <p>
                A publication collection, bundles 2 or more published datasets. <br>
            </p>
            <hr class="bg-white" />
            <p class="q-ma-none">
                Your selection does not meet that requirement.
            </p>
        </QBanner>
    </div>
</template>

<style scoped>
.dataset-title {
    font-size: medium;
    font-weight: bold;
}

.publication-card {
    display: flex;
    flex-direction: column;
    padding: 8px;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    color: inherit;
    text-decoration: none;
}

.publication-card:hover {
    color: #007BFF;
    cursor: pointer;
    border-color: #007BFF;
}
</style>
