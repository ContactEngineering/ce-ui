<script setup lang="ts">

import { computed, inject, onMounted, ref } from "vue";
import {
    QBanner,
    QBtn,
    QDialog,
    QCard,
    QCardSection,
    QCardActions,
    QSpinner,
    QTabs,
    QTab,
    QTabPanels,
    QTabPanel
} from "quasar";

import { useNotify } from "@/utils/notify";
import {
    managerApiTopographyRetrieve,
    managerApiTopographyDestroy,
    managerApiTopographyForceInspectCreate
} from "@/api";

import { getIdFromUrl, subjectsToBase64 } from "topobank/utils/api";

import Attachments from "../manager/Attachments.vue";

import DeepZoomImage from "../components/DeepZoomImage.vue";
import LineScanPlot from "../components/LineScanPlot.vue";

import TopographyBadges from "../manager/TopographyBadges.vue";
import TopographyCard from "../manager/TopographyCard.vue";

const { show } = useNotify();

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

onMounted(async () => {
    await updateCard(appProps.object);
});

async function updateCard(topography = null) {
    if (topography !== null) {
        _topography.value = topography;
        _disabled.value = _topography.value === null || _topography.value.permissions.current_user.permission === "view";
    }

    /* Fetch topography info from API endpoint if status is pending */
    if (["pe", "st"].includes(topography.task_state)) {
        try {
            const topographyId = getIdFromUrl(_topography.value.url);
            await managerApiTopographyRetrieve({path: {id: topographyId}});
        } catch (error) {
            show?.({
                props: {
                    title: "Failed to load measurement",
                    body: error,
                    variant: "danger"
                }
            });
        }
    }
}

async function deleteTopography() {
    try {
        const topographyId = getIdFromUrl(_topography.value.url);
        await managerApiTopographyDestroy({path: {id: topographyId}});
        const id = getIdFromUrl(_topography.value.surface);
        window.location.href = `/ui/dataset-detail/${id}/`;
    } catch (error) {
        show?.({
            props: {
                title: "Failed to delete measurement",
                body: error,
                variant: "danger"
            }
        });
    }
}

async function forceInspect() {
    try {
        const topographyId = getIdFromUrl(_topography.value.url);
        const response = await managerApiTopographyForceInspectCreate({path: {id: topographyId}});
        await updateCard(response.data);
    } catch (error) {
        show?.({
            props: {
                title: "Failed to create zoomable image",
                body: error,
                variant: "danger"
            }
        });
    }
}

const base64Subjects = computed(() => {
    return subjectsToBase64({
        topography: [_topography.value.id]
    });
});

const _activeTab = ref('visualization');

</script>

<template>
    <div class="container">
        <div v-if="_topography == null" class="flex justify-center q-mt-xl">
            <div class="column items-center">
                <QSpinner size="lg" />
                <p class="q-mt-sm">Loading...</p>
            </div>
        </div>
        <div v-if="_topography !== null" class="row">
            <div class="col-3">
                <QTabs v-model="_activeTab" vertical class="text-grey" active-color="primary">
                    <QTab name="visualization" label="Visualization" />
                    <QTab name="details" label="Details" />
                    <QTab name="attachments" label="Attachments" />
                </QTabs>
                <div class="q-mt-md column q-gutter-sm">
                    <QBtn color="positive" :href="`/ui/analysis-list/?subjects=${base64Subjects}`" label="Analyze" />
                    <QBtn color="grey-4" text-color="dark" :href="_topography.datafile?.file" label="Download" />
                    <QBtn color="negative" @click="_showDeleteModal = true" label="Delete" />
                </div>
                <QCard class="q-mt-md">
                    <QCardSection>
                        <topography-badges :topography="_topography" />
                    </QCardSection>
                </QCard>
            </div>
            <div class="col-9">
                <QTabPanels v-model="_activeTab" animated>
                    <QTabPanel name="visualization">
                        <QBanner v-if="_topography.deepzoom === null && _topography.size_y !== null" class="bg-warning text-white q-mb-md">
                            <p class="q-mb-sm">This measurement does not have a zoomable image.</p>
                            <QBtn color="secondary" label="Retry creation of zoomable image" @click="forceInspect" />
                        </QBanner>
                        <LineScanPlot v-if="_topography.size_y === null" :topography="_topography" />
                        <DeepZoomImage v-if="_topography.deepzoom !== null && _topography.size_y !== null"
                                       :colorbar="true"
                                       :folder-url="_topography.deepzoom" />
                    </QTabPanel>
                    <QTabPanel name="details">
                        <TopographyCard :topography-url="_topography.url"
                                        v-model:topography="_topography"
                                        :enlarged="true"
                                        :disabled="_disabled" />
                    </QTabPanel>
                    <QTabPanel name="attachments">
                        <Attachments :attachments-url="_topography.attachments"
                                     :permission="_topography.permissions.current_user.permission" />
                    </QTabPanel>
                </QTabPanels>
            </div>
        </div>
    </div>
    <QDialog v-if="_topography !== null" v-model="_showDeleteModal">
        <QCard>
            <QCardSection>
                <div class="text-h6">Delete measurement</div>
            </QCardSection>
            <QCardSection>
                You are about to delete the measurement with name <b>{{ _topography.name }}</b>.
                Are you sure you want to proceed?
            </QCardSection>
            <QCardActions align="right">
                <QBtn flat label="Cancel" v-close-popup />
                <QBtn color="negative" label="Delete" @click="deleteTopography" v-close-popup />
            </QCardActions>
        </QCard>
    </QDialog>
</template>
