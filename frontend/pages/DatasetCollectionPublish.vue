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

const appProps = inject("appProps") as any;
const datasets = ref<any[]>([]);
const publications = ref<any[]>([]);
const title = ref("");
const validTitle = ref<boolean | null>(null);
const description = ref("");
const pending_request = ref(false);
const { show } = useToastController();

const datasetIds = appProps?.searchParams?.getAll("dataset") || [];
const invalid_id = ref(false);

datasetIds.forEach((datasetId: string) => {
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
                    body: `The dataset with ID:${datasetId} is not published.`,
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

function datetimeToDateString(timestamp: string) {
    const date = new Date(timestamp);
    return date.toISOString().substring(0, 10);
}

function publish() {
    validTitle.value = title.value !== "";
    if (validTitle.value) {
        pending_request.value = true;
        axios.post('/go/publish-collection/', {
            publication: publications.value.map(publication => publication.id),
            title: title.value,
            description: description.value
        }).then((response) => {
            window.location.href = `/ui/dataset-collection/${response.data.collection_id}/`;
        }).catch((err) => {
            console.error(err.response?.statusText);
            pending_request.value = false;
            show?.({
                props: {
                    title: "Publishing failed",
                    body: err.response?.statusText || "An error occurred",
                    variant: 'danger'
                }
            });
        });
    }
}

const validSelection = computed(() => {
    return datasetIds.length > 1 && !invalid_id.value;
});

// A collection is a citable record like any other publication, so the server
// requires the publisher to have a connected ORCID account.
const hasOrcid = appProps?.userHasOrcid ?? false;
const connectionsUrl = appProps?.connectionsUrl ?? "/accounts/3rdparty/";

</script>
<template>
    <div class="container py-4">
        <div class="card shadow border-0 rounded-4 overflow-hidden">
            <div class="card-header bg-primary text-white p-4">
                <h2 class="h4 fw-bold mb-1"><i class="fa-solid fa-layer-group me-2"></i>Publish a Collection</h2>
                <p class="mb-0 text-white-50 small">Bundle multiple published datasets into a cited collection release under CC0 1.0.</p>
            </div>

            <div class="card-body p-4 p-md-5">
                <BAlert v-if="!hasOrcid" :model-value="true" variant="danger" class="shadow-sm">
                    <h4 class="alert-heading fw-bold">
                        <i class="fa-solid fa-circle-exclamation me-2"></i>An ORCID iD is required to publish
                    </h4>
                    <p>
                        Publishing creates a permanent, citable record, so its authors have to be
                        identifiable as researchers. Connect your ORCID account to this profile
                        and come back.
                    </p>
                    <a :href="connectionsUrl" class="btn btn-danger mb-0">Connect your ORCID iD</a>
                </BAlert>

                <div v-else-if="validSelection">
                    <BAlert :model-value="true" variant="warning" class="border-warning-subtle bg-warning-subtle text-warning-emphasis mb-4 shadow-sm">
                        <h5 class="alert-heading fw-bold mb-2">
                            <i class="fa-solid fa-triangle-exclamation me-2"></i>Publication Collection Agreement
                        </h5>
                        <p class="mb-2">
                            A publication collection bundles 2 or more already published datasets into a single collection object.<br>
                            The collection will be published under the 
                            <a href="https://creativecommons.org/publicdomain/zero/1.0/" target="_blank" rel="noopener" class="fw-semibold">
                                CC0 1.0 Universal License <i class="fa-solid fa-external-link small"></i>
                            </a>.<br>
                            You will be designated as the primary author of this collection.
                        </p>
                    </BAlert>

                    <div class="mb-4">
                        <label for="collection-title" class="form-label fw-bold">Collection Title <span class="text-danger">*</span></label>
                        <BFormInput id="collection-title" v-model="title" :state="validTitle"
                            placeholder="e.g. Surface topography measurements of worn steel samples" size="lg" />
                        <small v-if="validTitle === false" class="text-danger mt-1 d-block">Please enter a collection title.</small>
                    </div>

                    <div class="mb-4">
                        <label for="collection-desc" class="form-label fw-bold">Description</label>
                        <BFormTextarea id="collection-desc" v-model="description" placeholder="Provide a summary of the scope and context of this collection..." rows="3" />
                    </div>

                    <div class="mb-4">
                        <label class="form-label fw-bold mb-2">Included Publications ({{ datasets.length }})</label>
                        <div class="row g-3">
                            <div v-for="(dataset, index) in datasets" :key="dataset.id" class="col-md-6 col-lg-4">
                                <div class="card h-100 border shadow-sm hover-shadow transition-all">
                                    <div class="card-body p-3">
                                        <h6 class="card-title fw-bold text-primary text-truncate mb-2">
                                            <i class="fa-solid fa-layer-group me-1"></i> {{ dataset.name }}
                                        </h6>
                                        <p class="card-text small text-muted mb-1" v-if="publications[index]">
                                            <i class="fa-solid fa-user me-1"></i> Publisher: {{ publications[index].publisher?.name }}
                                        </p>
                                        <p class="card-text small text-muted mb-3" v-if="publications[index]">
                                            <i class="fa-solid fa-calendar me-1"></i> Published: {{ datetimeToDateString(publications[index].datetime) }}
                                        </p>
                                        <a :href="`/ui/dataset-detail/${dataset.id}/`" target="_blank" class="btn btn-sm btn-outline-primary w-100">
                                            View Dataset <i class="fa-solid fa-arrow-up-right-from-square ms-1"></i>
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="d-flex justify-content-end pt-3 border-top">
                        <BButton v-if="pending_request" disabled variant="success" size="lg" class="px-4">
                            <BSpinner small class="me-2" /> Publishing Collection...
                        </BButton>
                        <BButton v-else @click="publish()" variant="success" size="lg" class="px-4 fw-bold shadow-sm">
                            Publish Collection 🚀
                        </BButton>
                    </div>
                </div>

                <BAlert v-else :model-value="true" variant="danger" class="shadow-sm">
                    <h4 class="alert-heading fw-bold"><i class="fa-solid fa-circle-exclamation me-2"></i>Invalid Selection</h4>
                    <p class="mb-0">
                        A publication collection requires 2 or more published datasets. Please return to the dataset manager and select multiple published datasets to continue.
                    </p>
                </BAlert>
            </div>
        </div>
    </div>
</template>
