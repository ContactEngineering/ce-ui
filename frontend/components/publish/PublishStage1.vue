<script setup lang="ts">

import { BButton, BCard, BSpinner } from 'bootstrap-vue-next';
import { ref } from 'vue';
import axios from "axios";

const props = defineProps({
    stage: Number,
    surfaceId: Number
});

const emit = defineEmits(['continue']);

const surface = ref();
const error = ref(false);
const loading = ref(true);

axios.get(`/manager/api/surface/${props.surfaceId}`).then((response) => {
    surface.value = response.data;
    loading.value = false;
}).catch((err) => {
    error.value = true;
    loading.value = false;
    console.error(err);
});
</script>

<template>
    <div v-if="props.stage == 0" class="stage-container">
        <div v-if="loading" class="text-center py-5">
            <BSpinner variant="primary" label="Loading dataset details..." />
            <p class="text-muted mt-2">Loading digital twin details...</p>
        </div>

        <div v-else-if="surface && !error">
            <div class="card border-warning-subtle bg-warning-subtle p-4 mb-4 rounded-3 shadow-sm">
                <div class="d-flex align-items-start">
                    <div class="bg-warning text-dark p-3 rounded-circle me-3 flex-shrink-0">
                        <i class="fa-solid fa-triangle-exclamation fs-3"></i>
                    </div>
                    <div>
                        <h4 class="card-title text-dark fw-bold mb-2">
                            Publishing Digital Twin: {{ surface.name }}
                        </h4>
                        <p class="card-text text-dark-emphasis mb-0">
                            By publishing, you create an <strong>immutable public snapshot</strong> of this digital twin along with all its measurement datasets.
                            This snapshot receives a permanent version number and DOI URL for academic citations. It will be open and accessible to everyone.
                        </p>
                    </div>
                </div>
            </div>

            <BCard class="shadow-sm mb-4">
                <template #header>
                    <div class="d-flex align-items-center justify-content-between">
                        <h5 class="mb-0 fw-semibold text-primary">
                            <i class="fa-solid fa-layer-group me-2"></i>Dataset Overview
                        </h5>
                        <span class="badge bg-secondary">ID: {{ surface.id }}</span>
                    </div>
                </template>
                <div class="row g-3">
                    <div class="col-md-6">
                        <strong class="text-muted d-block small">Name</strong>
                        <span class="fs-6 fw-medium">{{ surface.name }}</span>
                    </div>
                    <div class="col-md-6" v-if="surface.category">
                        <strong class="text-muted d-block small">Category</strong>
                        <span>{{ surface.category }}</span>
                    </div>
                    <div class="col-12" v-if="surface.description">
                        <strong class="text-muted d-block small">Description</strong>
                        <span>{{ surface.description }}</span>
                    </div>
                    <div class="col-md-6" v-if="surface.tags && surface.tags.length">
                        <strong class="text-muted d-block small mb-1">Tags</strong>
                        <span v-for="tag in surface.tags" :key="tag" class="badge bg-light text-dark border me-1">
                            {{ tag }}
                        </span>
                    </div>
                </div>
            </BCard>

            <div class="d-flex justify-content-end">
                <BButton @click="emit('continue')" variant="primary" size="lg" class="px-4">
                    Continue to Authors <i class="fa-solid fa-arrow-right ms-2"></i>
                </BButton>
            </div>
        </div>

        <div v-else-if="error" class="alert alert-danger p-4 rounded-3 shadow-sm">
            <div class="d-flex align-items-center">
                <i class="fa-solid fa-circle-exclamation fs-3 me-3"></i>
                <div>
                    <h5 class="alert-heading fw-bold mb-1">Digital Surface Twin Not Found</h5>
                    <p class="mb-0">Could not retrieve dataset details for ID {{ surfaceId }}. Please check the URL or try again later.</p>
                </div>
            </div>
        </div>
    </div>
</template>
