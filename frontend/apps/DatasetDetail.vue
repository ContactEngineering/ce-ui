<script setup lang="ts">

import { computed, inject, onMounted, ref, shallowRef } from "vue";

import {
    QExpansionItem,
    QBanner,
    QBadge,
    QCard,
    QCardSection,
    QBtnDropdown,
    QList,
    QItem,
    QItemSection,
    QCheckbox,
    QDialog,
    QCardActions,
    QSpinner,
    QBtn,
    QSeparator,
    QTabs,
    QTab,
    QTabPanels,
    QTabPanel,
    QSpace,
    QScrollArea,
    ClosePopup
} from 'quasar';

const vClosePopup = ClosePopup;

import { useNotify } from "@/utils/notify";
import {
    goPublicationList,
    goPublicationRetrieve,
    managerApiSurfaceDestroy,
    managerApiTopographyCreate,
    managerApiTopographyPartialUpdate
} from "@/api";

import {
    filterTopographyForPatchRequest,
    getIdFromUrl,
    subjectsToBase64
} from "../utils/api";
import { ccLicenseInfo } from "../utils/data";

import ActionFab from '../components/ActionFab.vue';
import type { FabAction } from '../components/ActionFab.vue';
import Attachments from '../manager/Attachments.vue';
import BandwidthPlot from '../manager/BandwidthPlot.vue';
import DatasetDescription from '../manager/DatasetDescription.vue';
import DatasetPermissions from '../manager/DatasetPermissions.vue';
import DatasetProperties from '../manager/DatasetProperties.vue';
import TopographyListRow from "../manager/TopographyListRow.vue";
import TopographyUpdateCard from "../manager/TopographyUpdateCard.vue";
import UploadModal from '../components/UploadModal.vue';

const { show } = useNotify();

const props = defineProps({
    categories: {
        type: Object,
        default: {
            dum: 'Dummy data',
            exp: 'Experimental data',
            sim: 'Simulated data'
        }
    }
});

const appProps = inject("appProps");

const emit = defineEmits([
    'delete:surface'
])

const attachmentCount = ref(null);  // default count of the attachments 

const propertyCount = ref(null);  // default count of the properties

// Data that is displayed or can be edited
const _surface = shallowRef(null);  // Surface data
const _publication = ref(null);  // Publication data
const _permissions = ref(null);  // Permissions
const _topographies = ref([]);  // Topographies contained in this surface
const _versions = ref(null);  // Published versions of this surface

// GUI logic
const _saving = ref(false);  // Saving batch edits
const _showDeleteModal = ref(false);  // Triggers delete modal
const _selected = ref([]);  // Selected topographies (for batch editing)

// Batch edit data
const _batchEditTopography = ref(emptyTopography());

// Upload modal
const _showUploadModal = ref(false);
const _showAttachmentModal = ref(false);

function emptyTopography() {
    return {
        url: null,  // There is no representation of this topography on the server side
        name: null,
        channel_names: null,
        description: null,
        measurement_date: null,
        size_editable: true,
        size_x: null,
        size_y: null,
        unit_editable: true,
        unit: null,
        height_scale_editable: true,
        height_scale: null,
        fill_undefined_surface_mode: null,
        detrend_mode: null,
        is_periodic: null,
        instrument_name: null,
        instrument_type: null,
        instrument_parameters: null,
        thumbnail: null,
        tags: []
    };
}

onMounted(() => {
    if (_surface.value == null) {
        updateCard();
    }
});

function getSurfaceId() {
    return getIdFromUrl(_surface.value.url);
}

function getOriginalSurfaceId() {
    if (_publication.value == null) {
        return getIdFromUrl(_surface.value.url);
    } else {
        return getIdFromUrl(_publication.value.original_surface);
    }
}

function updateCard() {
    /* Fetch JSON describing the card */
    _surface.value = appProps.object;
    _permissions.value = appProps.object.permissions;
    _topographies.value = appProps.object.topography_set;
    _selected.value = new Array(_topographies.value.length).fill(false);  // Nothing is selected
    updatePublication();
}

async function updatePublication() {
    if (_surface.value.publication == null) {
        _publication.value = null;
        updateVersions();
    } else {
        try {
            const publicationId = getIdFromUrl(_surface.value.publication);
            const response = await goPublicationRetrieve({path: {id: publicationId}});
            _publication.value = response.data;
            updateVersions();
        } catch (error) {
            show?.({
                props: {
                    title: "Failed to fetch publication information",
                    body: error,
                    variant: 'danger'
                }
            });
        }
    }
}

async function updateVersions() {
    try {
        const response = await goPublicationList({
            query: {original_surface: getOriginalSurfaceId()} as any
        });
        _versions.value = response.data;
    } catch (error) {
        show?.({
            props: {
                title: "Failed to fetch published versions",
                body: error,
                variant: 'danger'
            }
        });
    }
}

function onTopographiesUploaded(results: any[]) {
    // Add uploaded topographies to the list
    for (const result of results) {
        // The topography object from the upload already has the file attached
        // but we don't need the file reference anymore since it's uploaded
        const topography = result.topography;
        delete topography.file;
        delete topography.datafile?.upload_instructions;
        _topographies.value.push(topography);
        _selected.value.push(false);  // initially unselected
    }
}

function deleteTopography(index) {
    _topographies.value[index] = null;
}    

async function saveBatchEdit(topography) {
    // Trigger saving spinner
    _saving.value = true;

    // Clear all null fields
    const cleanedBatchEditTopography = filterTopographyForPatchRequest(topography);

    // Update all topographies and issue patch request
    const updatePromises = [];
    for (const i in _topographies.value) {
        if (_selected.value[i]) {
            const t = {
                ..._topographies.value[i],
                ...cleanedBatchEditTopography
            }
            const topographyId = getIdFromUrl(t.url);
            const updatePromise = managerApiTopographyPartialUpdate({
                path: {id: topographyId},
                body: filterTopographyForPatchRequest(t)
            }).then(response => {
                _topographies.value[i] = response.data;
            }).catch(error => {
                show?.({
                    props: {
                        title: "Failed to update measurement",
                        body: error,
                        variant: 'danger'
                    }
                });
            });
            updatePromises.push(updatePromise);
        }
    }

    // Wait for all updates to complete
    await Promise.all(updatePromises);

    // Reset selection
    _selected.value.fill(false);

    // Reset the batch edit topography template
    _batchEditTopography.value = emptyTopography();

    // Saving is done
    _saving.value = false;
}

function discardBatchEdit() {
    // Reset selection
    _selected.value.fill(false);

    // Reset the batch edit topography template
    _batchEditTopography.value = emptyTopography();
}

function surfaceHrefForVersion(version) {
    return `/ui/dataset-detail/${getIdFromUrl(version.surface)}/`;
}

async function deleteSurface() {
    try {
        const surfaceId = getIdFromUrl(_surface.value.url);
        await managerApiSurfaceDestroy({path: {id: surfaceId}});
        emit('delete:surface', _surface.value.url);
        window.location.href = `/ui/dataset-list/`;
    } catch (error) {
        show?.({
            props: {
                title: "Failed to delete digital surface twin",
                body: error,
                variant: 'danger'
            }
        });
    }
}

const base64Subjects = computed(() => {
    return subjectsToBase64({surface: [_surface.value.id]});
});

const versionString = computed(() => {
    if (_surface.value == null || _publication.value == null) {
        return "Work in progress";
    } else {
        return `Version ${_publication.value.version} (${_publication.value.datetime.slice(0, 10)})`;
    }
});

const hrefOriginalSurface = computed(() => {
    return `/ui/dataset-detail/${getOriginalSurfaceId()}/`;
});

const publishUrl = computed(() => {
    return `/ui/dataset-publish/${getSurfaceId()}/`;
});

const isEditable = computed(() => {
    return _surface.value != null && _surface.value.permissions.current_user.permission !== 'view';
});

const hasFullAccess = computed(() => {
    return _surface.value != null && _surface.value.permissions.current_user.permission === 'full';
});

const isPublication = computed(() => {
    return _surface.value != null && _publication.value != null;
});

const anySelected = computed(() => {
    return _selected.value.reduce((x, y) => x || y, false);
});

const someSelected = computed(() => {
    const nbSelected = _selected.value.reduce((x, y) => x + (y ? 1 : 0), 0);
    const nbTopographies = _topographies.value.reduce((x, y) => x + (y != null ? 1 : 0), 0);
    return nbSelected > 0 && nbSelected < nbTopographies;
});

const allSelected = computed({
    get() {
        return _selected.value.reduce((x, y) => x && y, true);
    },
    set(value) {
        _selected.value.fill(value);
    }
});

const measurementCount = computed(() => {
  return _topographies.value.filter(t => t !== null).length;
});


const batchActiveTab = ref('home'); // shared active tab for batch mode

const _activeTab = ref('measurements'); // main navigation tab

// FAB actions
const fabActions = computed<FabAction[]>(() => {
    const actions: FabAction[] = [];

    if (isEditable.value) {
        actions.push({
            id: 'upload',
            icon: 'upload_file',
            label: 'Upload measurements',
            color: 'primary',
            tooltip: 'Upload new measurement files'
        });
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
        href: `${_surface.value?.url}download/`
    });

    actions.push({
        id: 'analyze',
        icon: 'analytics',
        label: 'Analyze',
        color: 'accent',
        href: `/ui/analysis-list/?subjects=${base64Subjects.value}`
    });

    if (!isPublication.value && hasFullAccess.value) {
        actions.push({
            id: 'publish',
            icon: 'publish',
            label: 'Publish',
            href: publishUrl.value
        });
    }

    if ((_versions.value === null || _versions.value.length === 0) && hasFullAccess.value) {
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
        case 'upload':
            _showUploadModal.value = true;
            break;
        case 'attach':
            _activeTab.value = 'attachments';
            _showAttachmentModal.value = true;
            break;
        case 'delete':
            _showDeleteModal.value = true;
            break;
    }
}

function navigateToTopography(topography: any) {
    const id = getIdFromUrl(topography.url);
    window.location.href = `/ui/topography/${id}/`;
}

</script>

<template>
    <div v-if="_surface == null" class="flex justify-center q-mt-xl">
        <div class="column items-center">
            <QSpinner size="lg" />
            <p class="q-mt-sm">Loading...</p>
        </div>
    </div>
    <div v-if="_surface != null">
        <!-- Page Header with Badges and Version -->
        <div class="row items-center q-mb-md">
            <div class="col row items-center q-gutter-sm">
                <QBadge v-if="_publication != null" color="info">
                    Published
                </QBadge>
                <QBadge v-for="tag in _surface.tags" :key="tag.name" color="positive">
                    {{ tag.name }}
                </QBadge>
                <span v-if="_publication != null" class="text-caption text-grey-7">
                    Published by {{ _publication.publisher.name }}
                </span>
            </div>
            <QBtnDropdown v-if="_versions == null || _versions.length > 0"
                          :label="versionString"
                          flat
                          dense>
                <QList>
                    <QItem v-if="_publication == null || _publication.has_access_to_original_surface"
                           clickable v-close-popup
                           :disable="_publication == null"
                           :href="hrefOriginalSurface">
                        <QItemSection>Work in progress</QItemSection>
                    </QItem>
                    <QItem v-if="_versions == null">
                        <QItemSection><QSpinner size="xs" /> Loading...</QItemSection>
                    </QItem>
                    <QItem v-for="version in _versions"
                           :key="version.version"
                           clickable v-close-popup
                           :disable="_publication != null && _publication.version === version.version"
                           :href="surfaceHrefForVersion(version)">
                        <QItemSection>Version {{ version.version }}</QItemSection>
                    </QItem>
                </QList>
            </QBtnDropdown>
        </div>

        <!-- Navigation Tabs -->
        <QTabs v-model="_activeTab" dense align="left" class="text-grey" active-color="primary" indicator-color="primary" narrow-indicator>
            <QTab name="measurements">
                <span class="row items-center no-wrap">
                    Measurements
                    <QBadge color="grey-5" text-color="white" class="q-ml-xs">{{ measurementCount }}</QBadge>
                </span>
            </QTab>
            <QTab name="bandwidths" label="Bandwidths" />
            <QTab name="description" label="Description" />
            <QTab v-if="propertyCount !== 0 || isEditable" name="properties">
                <span class="row items-center no-wrap">
                    Properties
                    <QBadge color="grey-5" text-color="white" class="q-ml-xs">{{ propertyCount }}</QBadge>
                </span>
            </QTab>
            <QTab v-if="attachmentCount === null || attachmentCount !== 0 || isEditable" name="attachments">
                <span class="row items-center no-wrap">
                    Attachments
                    <QBadge color="grey-5" text-color="white" class="q-ml-xs">{{ attachmentCount }}</QBadge>
                </span>
            </QTab>
            <QTab name="permissions" label="Permissions" />
            <QTab v-if="isPublication" name="citation" label="Cite" />
        </QTabs>

        <QSeparator class="q-mb-md" />

        <!-- Tab Panels -->
        <QTabPanels v-model="_activeTab" animated>
            <!-- Measurements -->
            <QTabPanel name="measurements" class="q-pa-none">
                <!-- Batch edit panel -->
                <TopographyUpdateCard v-if="anySelected"
                                      v-model:topography="_batchEditTopography"
                                      v-model:active-tab="batchActiveTab"
                                      :batch-edit="true"
                                      :saving="_saving"
                                      @save:edit="saveBatchEdit"
                                      @discard:edit="discardBatchEdit" />

                <!-- Select all checkbox -->
                <div v-if="isEditable && _topographies.length > 0" class="q-mb-sm q-pa-sm bg-grey-2 rounded-borders">
                    <QCheckbox v-model="allSelected"
                               :indeterminate-value="someSelected ? null : undefined"
                               label="Select all"
                               size="sm" />
                </div>

                <!-- Empty state -->
                <QBanner v-if="_topographies.length === 0" class="bg-grey-2 text-grey-8">
                    No measurements yet. Use the upload button to add measurement files.
                </QBanner>

                <!-- Measurements list -->
                <QScrollArea v-if="_topographies.length > 0"
                             style="height: calc(100vh - 350px); min-height: 300px;"
                             class="rounded-borders">
                    <QList bordered separator class="rounded-borders">
                        <template v-for="(topography, index) in _topographies" :key="topography?.url || index">
                            <TopographyListRow v-if="topography != null"
                                               :topography="topography"
                                               :selectable="isEditable"
                                               :disabled="!isEditable"
                                               v-model:selected="_selected[index]"
                                               @click="navigateToTopography" />
                        </template>
                    </QList>
                </QScrollArea>
            </QTabPanel>

            <!-- Bandwidths -->
            <QTabPanel name="bandwidths" class="q-pa-none">
                <QBanner v-if="_topographies.length == 0" class="bg-info text-white q-mb-md">
                    This surface has no measurements.
                </QBanner>
                <QBanner v-if="_topographies.length > 0" class="bg-grey-2 q-mb-md">
                    This bandwidth plot shows the range of length scales that have been measured for
                    this digital surface twin. Each of the blocks below represents one measurement.
                    Part of the bandwidth shown may be unreliable due to the configured instrument's
                    measurement capacities.
                </QBanner>
                <bandwidth-plot v-if="_topographies.length > 0" :topographies="_topographies" />
            </QTabPanel>

            <!-- Description -->
            <QTabPanel name="description" class="q-pa-none">
                <DatasetDescription v-if="_surface != null"
                                    :description="_surface.description"
                                    :name="_surface.name"
                                    :permission="_permissions.current_user.permission"
                                    :surface-url="_surface.url"
                                    :tags="_surface.tags" />
            </QTabPanel>

            <!-- Properties -->
            <QTabPanel name="properties" class="q-pa-none">
                <DatasetProperties v-if="_surface != null"
                                   v-model:properties="_surface.properties"
                                   :permission="_permissions.current_user.permission"
                                   :surface-url="_surface.url"
                                   v-model:propertyCount="propertyCount" />
            </QTabPanel>

            <!-- Attachments -->
            <QTabPanel name="attachments" class="q-pa-none">
                <Attachments v-if="_surface != null"
                             :attachments-url="_surface.attachments"
                             :permission="_permissions.current_user.permission"
                             v-model:attachmentCount="attachmentCount" />
            </QTabPanel>

            <!-- Permissions -->
            <QTabPanel name="permissions" class="q-pa-none">
                <DatasetPermissions v-if="_surface.publication == null"
                                    v-model:permissions="_permissions"
                                    :set-permissions-url="_surface.api.set_permissions" />
                <div v-if="_surface.publication != null">
                    <p>
                        This dataset is published. It is visible to everyone
                        (even without logging into the system) and can no longer be modified.
                    </p>
                </div>
            </QTabPanel>

            <!-- Citation -->
            <QTabPanel v-if="isPublication" name="citation" class="q-pa-none">
                <p class="q-mb-lg">
                    <a :href="ccLicenseInfo[_publication.license].descriptionUrl">
                        <img :src="`/static/images/cc/${_publication.license}.svg`"
                             :alt="ccLicenseInfo[_publication.license].title"
                             :title="`Dataset can be reused under the terms of the ${ccLicenseInfo[_publication.license].title}.`"
                             style="float:right; margin-left: 0.25rem;"/>
                    </a>
                    This dataset can be reused under the terms of the
                    <a :href="ccLicenseInfo[_publication.license].descriptionUrl">
                        {{ ccLicenseInfo[_publication.license].title }}
                    </a>.
                    When reusing this dataset, please cite the original source.
                </p>
                <QExpansionItem default-opened label="Citation" header-class="bg-grey-2">
                    <div class="q-pa-md" v-html="_publication.citation.html" />
                </QExpansionItem>
                <QExpansionItem label="RIS" header-class="bg-grey-2">
                    <div class="q-pa-md">
                        <pre class="q-ma-none">{{ _publication.citation.ris }}</pre>
                    </div>
                </QExpansionItem>
                <QExpansionItem label="BibTeX" header-class="bg-grey-2">
                    <div class="q-pa-md">
                        <pre class="q-ma-none">{{ _publication.citation.bibtex }}</pre>
                    </div>
                </QExpansionItem>
                <QExpansionItem label="BibLaTeX" header-class="bg-grey-2">
                    <div class="q-pa-md">
                        <pre class="q-ma-none">{{ _publication.citation.biblatex }}</pre>
                    </div>
                </QExpansionItem>
            </QTabPanel>
        </QTabPanels>
    </div>
    <!-- Floating Action Button -->
    <ActionFab v-if="_surface != null"
               :actions="fabActions"
               @action="handleFabAction" />

    <!-- Upload Modal for Measurements -->
    <UploadModal v-if="_surface != null"
                 v-model="_showUploadModal"
                 mode="topography"
                 :target-url="_surface.url"
                 @uploaded="onTopographiesUploaded" />

    <!-- Delete Confirmation Dialog -->
    <QDialog v-if="_surface != null" v-model="_showDeleteModal">
        <QCard>
            <QCardSection>
                <div class="text-h6">Delete digital surface twin</div>
            </QCardSection>
            <QCardSection>
                You are about to delete the digital surface twin with name <b>{{ _surface.name }}</b>
                and all contained measurements. Are you sure you want to proceed?
            </QCardSection>
            <QCardActions align="right">
                <QBtn flat label="Cancel" v-close-popup />
                <QBtn color="negative" label="Delete" @click="deleteSurface" v-close-popup />
            </QCardActions>
        </QCard>
    </QDialog>
</template>
