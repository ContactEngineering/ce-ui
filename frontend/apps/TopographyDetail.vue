<script setup lang="ts">

import { computed, inject, onMounted, ref } from "vue";
import {
    QBanner,
    QBtn,
    QDialog,
    QCard,
    QCardSection,
    QCardActions,
    QSeparator,
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

import ActionFab from '../components/ActionFab.vue';
import type { FabAction } from '../components/ActionFab.vue';
import Attachments from "../manager/Attachments.vue";
import DeepZoomImage from "../components/DeepZoomImage.vue";
import LineScanPlot from "../components/LineScanPlot.vue";
import TopographyBadges from "../manager/TopographyBadges.vue";
import TopographyCard from "../manager/TopographyCard.vue";
import UploadModal from '../components/UploadModal.vue';

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
const _showAttachmentModal = ref(false);
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

const surfaceUrl = computed(() => {
    const surfaceId = getIdFromUrl(_topography.value.surface);
    return `/ui/dataset-detail/${surfaceId}/`;
});

const _activeTab = ref('visualization');

// FAB actions
const fabActions = computed<FabAction[]>(() => {
    const actions: FabAction[] = [];

    if (!_disabled.value) {
        actions.push({
            id: 'attach',
            icon: 'attach_file',
            label: 'Add attachment',
            color: 'secondary',
            tooltip: 'Attach supporting files'
        });
    }

    actions.push({
        id: 'download',
        icon: 'download',
        label: 'Download',
        href: _topography.value?.datafile?.file
    });

    actions.push({
        id: 'analyze',
        icon: 'analytics',
        label: 'Analyze',
        color: 'accent',
        href: `/ui/analysis-list/?subjects=${base64Subjects.value}`
    });

    if (!_disabled.value) {
        actions.push({
            id: 'delete',
            icon: 'delete',
            label: 'Delete',
            color: 'negative'
        });
    }

    return actions;
});

function handleFabAction(actionId: string) {
    switch (actionId) {
        case 'attach':
            _activeTab.value = 'attachments';
            _showAttachmentModal.value = true;
            break;
        case 'delete':
            _showDeleteModal.value = true;
            break;
    }
}

</script>

<template>
    <div v-if="_topography == null" class="flex justify-center q-mt-xl">
        <div class="column items-center">
            <QSpinner size="lg" />
            <p class="q-mt-sm">Loading...</p>
        </div>
    </div>
    <div v-if="_topography !== null">
        <!-- Topography Info Chips -->
        <div class="q-mb-md">
            <TopographyBadges :topography="_topography" />
        </div>

        <!-- Navigation Tabs -->
        <QTabs v-model="_activeTab" dense align="left" class="text-grey" active-color="primary" indicator-color="primary" narrow-indicator>
            <QTab name="visualization" label="Visualization" />
            <QTab name="details" label="Details" />
            <QTab name="attachments" label="Attachments" />
        </QTabs>

        <QSeparator class="q-mb-md" />

        <!-- Tab Panels -->
        <QTabPanels v-model="_activeTab" animated>
            <QTabPanel name="visualization" class="q-pa-none">
                <QBanner v-if="_topography.deepzoom === null && _topography.size_y !== null" class="bg-warning text-white q-mb-md">
                    <p class="q-mb-sm">This measurement does not have a zoomable image.</p>
                    <QBtn color="secondary" label="Retry creation of zoomable image" @click="forceInspect" />
                </QBanner>
                <LineScanPlot v-if="_topography.size_y === null" :topography="_topography" />
                <DeepZoomImage v-if="_topography.deepzoom !== null && _topography.size_y !== null"
                               :colorbar="true"
                               :folder-url="_topography.deepzoom" />
            </QTabPanel>
            <QTabPanel name="details" class="q-pa-none">
                <TopographyCard :topography-url="_topography.url"
                                v-model:topography="_topography"
                                :enlarged="true"
                                :disabled="_disabled" />
            </QTabPanel>
            <QTabPanel name="attachments" class="q-pa-none">
                <Attachments :attachments-url="_topography.attachments"
                             :permission="_topography.permissions.current_user.permission" />
            </QTabPanel>
        </QTabPanels>
    </div>
    <!-- Floating Action Button -->
    <ActionFab v-if="_topography !== null"
               :actions="fabActions"
               @action="handleFabAction" />

    <!-- Upload Modal for Attachments -->
    <UploadModal v-if="_topography !== null"
                 v-model="_showAttachmentModal"
                 mode="attachment"
                 :target-url="_topography.attachments" />

    <!-- Delete Confirmation Dialog -->
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
