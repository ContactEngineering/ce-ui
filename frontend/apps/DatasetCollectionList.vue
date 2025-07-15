<script setup lang="ts">
import { ref, watchEffect } from "vue";
import axios from "axios";
    
import { BBadge, BPagination ,useToastController } from "bootstrap-vue-next";

const { show } = useToastController();
const props = defineProps({
    apiUrl: {
        type: String,
        default: "/go/publication-collection"
    },
})
const collections = ref([])
const itemsPerPage = 10;
let page = ref(1)
let collectionsCount = ref(0)

watchEffect(() => {
    axios.get(props.apiUrl + `/?limit=${itemsPerPage}&offset=${(page.value-1)*itemsPerPage}`)
        .then((result) => {
            collections.value = result.data.results;
            collectionsCount.value = result.data.count;
        }).catch((err) => {
        show?.({
            props: {
                title: "Error fetching collections",
                body: "Error while fetching publication collections",
                variant: 'danger'
            }
        });
        console.error("Error while fetching publication collections:\n", err);
        })
});

function openDetailView(id: number) {
    window.location.href = `/ui/dataset-collection/${id}/`
}

function doiUrl(doiName: string): string {
    return `https://doi.org/${doiName}`
}

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

</script>

<template>
    <div class="container">
        <div v-for="collection in collections" class="border rounded mb-2 p-3 highlight-on-hover"
            @click="openDetailView(collection.id)">
            <div class="d-flex align-items-center">
                <h3>{{ collection.title }}</h3>
                <BBadge v-if="collection.doi_name" class="ms-auto highlight-on-hover"
                    @click.stop="copyToClipboard(doiUrl(collection.doi_name))">
                    {{ doiUrl(collection.doi_name) }}
                </BBadge>
            </div>
            <p v-if="collection.description != ''">
                {{ collection.description }}
            </p>
            <span> This collection was published by {{ collection.publisher.name }}.</span><br>
            <span> It contains {{ collection.publications.length }} datasets.</span>
        </div>
    <div class="d-flex justify-content-center">
    <BPagination v-model="page"
                 :limit="9"
                 :per-page="itemsPerPage"
                 :total-rows="collectionsCount"
                 class="me-2 mb-0">
    </BPagination>
    </div>
    </div>
</template>

<style scoped>
.highlight-on-hover {
    border: 1px solid rgba(0, 0, 0, 0);
    transition: background-color 0.3s;
}

.highlight-on-hover:hover {
    border: 1px solid #000000;
    background: var(--bs-secondary-bg-subtle);
    cursor: pointer;
}
</style>
