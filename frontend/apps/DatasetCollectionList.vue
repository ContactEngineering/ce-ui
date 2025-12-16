<script setup lang="ts">
import { ref, watchEffect } from "vue";
import axios from "axios";

import { QBadge, QPagination } from "quasar";

import { useNotify } from "@/utils/notify";

const { show } = useNotify();
const props = defineProps({
    apiUrl: {
        type: String,
        default: "/go/publication-collection",
    },
});
const collections = ref([]);
const itemsPerPage = 7;
let page = ref(1);
let collectionsCount = ref(0);

watchEffect(() => {
    axios
        .get(
            props.apiUrl +
                `/?limit=${itemsPerPage}&offset=${(page.value - 1) * itemsPerPage}`,
        )
        .then((result) => {
            collections.value = result.data.results;
            collectionsCount.value = result.data.count;
        })
        .catch((err) => {
            show?.({
                props: {
                    title: "Error fetching collections",
                    body: "Error while fetching publication collections",
                    variant: "danger",
                },
            });
            console.error(
                "Error while fetching publication collections:\n",
                err,
            );
        });
});

function openDetailView(id: number) {
    window.location.href = `/ui/dataset-collection/${id}/`;
}

function doiUrl(doiName: string): string {
    return `https://doi.org/${doiName}`;
}

function copyToClipboard(text) {
    navigator.clipboard
        .writeText(text)
        .then(() => {
            show?.({
                props: {
                    title: "Copied",
                    body: "DOI url was copied to your system clippboard",
                    variant: "success",
                },
            });
        })
        .catch((err) => {
            console.error("Failed to copy:", err);
        });
}
</script>

<template>
    <div class="container">
        <div
            v-for="collection in collections"
            :key="collection.id"
            class="collection-card q-pa-md q-mb-md"
            @click="openDetailView(collection.id)"
        >
            <div class="flex items-center">
                <h3 class="q-ma-none">{{ collection.title }}</h3>
                <QBadge
                    v-if="collection.doi_name"
                    class="q-ml-auto highlight-on-hover"
                    @click.stop="copyToClipboard(doiUrl(collection.doi_name))"
                >
                    {{ doiUrl(collection.doi_name) }}
                </QBadge>
            </div>
            <p v-if="collection.description != ''" class="q-mt-sm">
                {{ collection.description }}
            </p>
            <span>
                This collection was published by {{ collection.publisher.name }}.
            </span><br />
            <span>
                It contains {{ collection.publications.length }} datasets.
            </span>
        </div>
        <div class="flex justify-center">
            <QPagination
                v-if="collectionsCount > itemsPerPage"
                v-model="page"
                :max="Math.ceil(collectionsCount / itemsPerPage)"
                :max-pages="9"
                boundary-links
                direction-links
            />
        </div>
    </div>
</template>

<style scoped>
.collection-card {
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    transition: background-color 0.3s, border-color 0.3s;
    cursor: pointer;
}

.collection-card:hover {
    border-color: #000000;
    background: #f5f5f5;
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
