<script setup lang="ts">

import { inject, ref } from "vue";

import { QBadge } from "quasar";

import { useNotify } from "@/utils/notify";
import {
    goPublicationCollectionRetrieve,
    goPublicationRetrieve,
    managerApiSurfaceRetrieve
} from "@/api";
import { getIdFromUrl } from "@/utils/api";

const { show } = useNotify();
const appProps = inject("appProps");

const collection = ref({});
const publications = ref([]);
const datasets = ref([]);

function datetimeToDateString(timestamp) {
    const date = new Date(timestamp);
    return date.toISOString().substring(0, 10);
}

async function loadCollection() {
    try {
        const collectionId = getIdFromUrl(appProps.object.url);
        const collectionResponse = await goPublicationCollectionRetrieve({path: {id: collectionId}});
        collection.value = collectionResponse.data;

        for (const publication_url of collectionResponse.data.publications) {
            try {
                const publicationId = getIdFromUrl(publication_url);
                const publicationResponse = await goPublicationRetrieve({path: {id: publicationId}});
                publications.value.push(publicationResponse.data);

                try {
                    const surfaceId = getIdFromUrl(publicationResponse.data.surface);
                    const surfaceResponse = await managerApiSurfaceRetrieve({path: {id: surfaceId}});
                    datasets.value.push(surfaceResponse.data);
                } catch {
                    show?.({
                        props: {
                            title: "API error",
                            body: `Dataset \"${publicationResponse.data.surface}\" could not be found.`,
                            variant: 'danger'
                        }
                    });
                }
            } catch {
                show?.({
                    props: {
                        title: "API error",
                        body: `Publication \"${publication_url}\" could not be found.`,
                        variant: 'danger'
                    }
                });
            }
        }
    } catch (err) {
        console.error(err);
        show?.({
            props: {
                title: "API error",
                body: `Publication Collection \"${appProps.object.url}\" could not be found.`,
                variant: 'danger'
            }
        });
    }
}

loadCollection();

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        show?.({
            props: {
                title: "Copied",
                body: "DOI url was copied to your system clippboard",
                variant: 'success'
            }
        });
    }).catch(err => {
        console.error("Failed to copy:", err);
    });
}

function doiUrl(doiName: string): string {
    return `https://doi.org/${doiName}`
}

</script>
<template>
    <div class="container">
        <div class="flex items-center">
            <h1 class="q-ma-none">{{ collection.title }}</h1>
            <QBadge v-if="collection.doi_name"
                    class="q-ml-auto highlight-on-hover"
                    @click.stop="copyToClipboard(doiUrl(collection.doi_name))">
                {{ doiUrl(collection.doi_name) }}
            </QBadge>
        </div>
        <p style="white-space: pre-wrap;" class="q-mt-md">
            {{ collection.description }}
        </p>
        <h2>Publications</h2>
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

.highlight-on-hover {
    border: 1px solid rgba(0, 0, 0, 0);
    transition: background-color 0.3s;
}

.highlight-on-hover:hover {
    border: 1px solid #000000;
    background: #e0e0e0;
    cursor: pointer;
}
</style>
