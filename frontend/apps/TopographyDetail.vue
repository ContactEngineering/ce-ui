<script setup lang="ts">

import axios from "axios";

import {computed, inject, onMounted, ref} from "vue";
import {
    BModal,
    BSpinner,
    BTab,
    BTabs,
    useToastController
} from "bootstrap-vue-next";

import {getIdFromUrl, subjectsToBase64} from "topobank/utils/api";

import Attachments from '../manager/Attachments.vue';

import DeepZoomImage from "../components/DeepZoomImage.vue";
import LineScanPlot from "../components/LineScanPlot.vue";

import TopographyBadges from "../manager/TopographyBadges.vue";
import TopographyCard from "../manager/TopographyCard.vue";

const {show} = useToastController();

const props = defineProps({
    topographyUrl: String,
    topographyUrlPrefix: {
        type: String,
        default: "/manager/api/topography/"
    }
});

const appProps = inject("appProps");

const _disabled = ref(false);
const _showDeleteModal = ref(false);
const _topography = ref(null);

function getTopographyUrl() {
    if (props.topographyUrl != null) {
        return props.topographyUrl;
    }
    const topographyId = appProps.searchParams.get("topography");
    return `${props.topographyUrlPrefix}${topographyId}`;
}

onMounted(() => {
    updateCard();
});

function updateCard() {
    /* Fetch JSON describing the card */
    /*
    axios.get(`${getTopographyUrl()}?permissions=yes&attachments=yes`).then(response => {
        _topography.value = response.data;
        _disabled.value = _topography.value === null || _topography.value.permissions.current_user.permission === 'view';
    }).catch(error => {
        show?.({
            props: {
                title: "Failed to fetch measurement",
                body: error,
                variant: 'danger'
            }
        });
    });
     */
    _topography.value = appProps.object;
    _disabled.value = _topography.value === null || _topography.value.permissions.current_user.permission === 'view';
}

function deleteTopography() {
    axios.delete(_topography.url).then(response => {
        this.$emit('topography-deleted', _topography.value.url);
        const id = getIdFromUrl(_topography.value.surface);
        window.location.href = `/ui/dataset-detail/${id}/`;
    }).catch(error => {
        show?.({
            props: {
                title: "Failed to delete measurement",
                body: error,
                variant: 'danger'
            }
        });
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
        <div v-if="_topography !== null"
             class="row">
            <div class="col-12">
                <BTabs class="nav-pills-custom"
                       content-class="w-100"
                       fill
                       pills
                       vertical>
                    <BTab title="Visualization">
                        <LineScanPlot v-if="_topography.size_y === null"
                                      :topography="_topography">
                        </LineScanPlot>
                        <DeepZoomImage v-if="_topography.size_y !== null"
                                       :colorbar="true"
                                       :folder-url="_topography.deepzoom">
                        </DeepZoomImage>
                    </BTab>
                    <BTab title="Details">
                        <TopographyCard :topography-url="_topography.url"
                                        v-model:topography="_topography"
                                        :enlarged="true"
                                        :disabled="_disabled">
                        </TopographyCard>
                    </BTab>
                    <BTab title="Attachments">
                        <Attachments :attachments-url="_topography.attachments"
                                     :permission="_topography.permissions.current_user.permission">
                        </Attachments>
                    </BTab>
                    <template #tabs-end>
                        <hr/>
                        <a :href="`/ui/analysis-list/?subjects=${base64Subjects}`"
                           class="btn btn-success mb-2 mt-2">
                            Analyze
                        </a>

                        <a :href="_topography.datafile?.file"
                           class="btn btn-light mb-2">
                            Download
                        </a>

                        <a href="#"
                           class="btn btn-danger mb-2"
                           @click="_showDeleteModal = true">
                            Delete
                        </a>
                        <hr/>
                        <div class="card mt-2">
                            <div class="card-body">
                                <topography-badges
                                    :topography="_topography"></topography-badges>
                            </div>
                        </div>
                    </template>
                </BTabs>
            </div>
        </div>
    </div>
    <BModal v-if="_topography !== null"
            v-model="_showDeleteModal"
            @ok="deleteTopography"
            title="Delete measurement">
        You are about to delete the measurement with name <b>{{ _topography.name }}</b>.
        Are you sure you want to proceed?
    </BModal>
</template>
