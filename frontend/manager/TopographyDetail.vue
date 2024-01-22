<script setup>

import axios from "axios";

import {computed, onMounted, ref, watch} from "vue";
import {BAlert, BModal, BSpinner, BTab, BTabs} from "bootstrap-vue-next";

import {getIdFromUrl, subjectsToBase64} from "topobank/utils/api.js";

import DeepZoomImage from "../components/DeepZoomImage.vue";
import LineScanPlot from "../components/LineScanPlot.vue";

import TopographyBadges from "./TopographyBadges.vue";
import TopographyCard from "./TopographyCard.vue";


const props = defineProps({
    topographyUrl: String
});

const _disabled = ref(false);
const _error = ref(null);
const _showDeleteModal = ref(false);
const _topography = ref(null);

onMounted(() => {
    updateCard();
});

function updateCard() {
    /* Fetch JSON describing the card */
    axios.get(`${props.topographyUrl}?permissions=yes`).then(response => {
        _topography.value = response.data;
        _disabled.value = _topography.value === null || _topography.value.permissions.current_user.permission === 'view';
    }).catch(error => {
        _error.value = error;
    });
}

function deleteTopography() {
    axios.delete(_topography.url).then(response => {
        this.$emit('topography-deleted', _topography.value.url);
        const id = getIdFromUrl(_topography.value.surface);
        window.location.href = `/ui/html/surface/?surface=${id}`;
    }).catch(error => {
        _error.value = error;
    });
}

const base64Subjects = computed(() => {
    return subjectsToBase64({
        topography: [_topography.value.id]
    });
});

</script>

<template>
    <div class="container">
        <div v-if="_topography == null"
             class="d-flex justify-content-center mt-5">
            <div class="flex-column text-center">
                <b-spinner/>
                <p>Loading...</p>
            </div>
        </div>
        <b-alert :model-value="_error != null"
                 variant="danger">
            {{ _error.message }}: {{ _error.response.statusText }}
        </b-alert>
        <div v-if="_topography !== null"
             class="row">
            <div class="col-12">
                <b-tabs class="nav-pills-custom"
                        content-class="w-100"
                        fill
                        pills
                        vertical>
                    <b-tab title="Visualization">
                        <line-scan-plot v-if="_topography.size_y === null"
                                        :topography="_topography">
                        </line-scan-plot>
                        <deep-zoom-image v-if="_topography.size_y !== null"
                                         :colorbar="true"
                                         :prefix-url="`${_topography.url}dzi/`">
                        </deep-zoom-image>
                    </b-tab>
                    <b-tab title="Properties">
                        <topography-card :topography-url="_topography.url"
                                         v-model:topography="_topography"
                                         :enlarged="true"
                                         :disabled="_disabled">
                        </topography-card>
                    </b-tab>
                    <template #tabs-end>
                        <hr/>
                        <a :href="`/ui/html/analysis-list/?subjects=${base64Subjects}`"
                           class="btn btn-outline-danger mb-2 mt-2">
                            Analyze
                        </a>

                        <a :href="_topography.datafile"
                           class="btn btn-outline-secondary mb-2">
                            Download
                        </a>

                        <a href="#"
                           class="btn btn-outline-secondary mb-2"
                           @click="_showDeleteModal = true">
                            Delete
                        </a>
                        <hr/>
                        <div class="card mt-2">
                            <div class="card-body">
                                <topography-badges :topography="_topography"></topography-badges>
                            </div>
                        </div>
                    </template>
                </b-tabs>
            </div>
        </div>
    </div>
    <b-modal v-if="_topography !== null"
             v-model="_showDeleteModal"
             @ok="deleteTopography"
             title="Delete measurement">
        You are about to delete the measurement with name <b>{{ _topography.name }}</b>.
        Are you sure you want to proceed?
    </b-modal>
</template>
