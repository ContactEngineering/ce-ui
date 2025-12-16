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
    QItemLabel,
    QCheckbox,
    QDialog,
    QCardActions,
    QSpinner,
    QBtn,
    QSeparator,
    QIcon
} from 'quasar';

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

import Attachments from '../manager/Attachments.vue';
import BandwidthPlot from '../manager/BandwidthPlot.vue';
import DropZone from '../components/DropZone.vue';
import DatasetDescription from '../manager/DatasetDescription.vue';
import DatasetPermissions from '../manager/DatasetPermissions.vue';
import DatasetProperties from '../manager/DatasetProperties.vue';
import TopographyCard from "../manager/TopographyCard.vue";
import TopographyUpdateCard from "../manager/TopographyUpdateCard.vue";

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

function filesDropped(files) {
    for (const file of files) {
        uploadNewTopography(file);
    }
}

async function uploadNewTopography(file) {
    try {
        const response = await managerApiTopographyCreate({
            body: {
                surface: _surface.value.url,
                name: file.name
            }
        });
        let upload = response.data;
        upload.file = file;  // need to know which file to upload
        _topographies.value.push(upload);  // this will trigger showing a topography-upload-card
        _selected.value.push(false);  // initially unselected
    } catch (error) {
        show?.({
            props: {
                title: "Failed to create a new measurement",
                body: error,
                variant: 'danger'
            }
        });
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

</script>

<template>
    <div v-if="_surface == null" class="flex justify-center q-mt-xl">
        <div class="column items-center">
            <QSpinner size="lg" />
            <p class="q-mt-sm">Loading...</p>
        </div>
    </div>
    <div v-if="_surface != null" class="row no-wrap">
        <!-- Left Sidebar -->
        <div class="sidebar q-pr-md" style="width: 240px; flex-shrink: 0;">
            <!-- Navigation -->
            <QList>
                <QItem clickable :active="_activeTab === 'measurements'" @click="_activeTab = 'measurements'">
                    <QItemSection avatar>
                        <QIcon name="science" />
                    </QItemSection>
                    <QItemSection>
                        <QItemLabel>Measurements</QItemLabel>
                    </QItemSection>
                    <QItemSection side>
                        <QBadge>{{ measurementCount }}</QBadge>
                    </QItemSection>
                </QItem>
                <QItem clickable :active="_activeTab === 'bandwidths'" @click="_activeTab = 'bandwidths'">
                    <QItemSection avatar>
                        <QIcon name="straighten" />
                    </QItemSection>
                    <QItemSection>
                        <QItemLabel>Bandwidths</QItemLabel>
                    </QItemSection>
                </QItem>
                <QItem clickable :active="_activeTab === 'description'" @click="_activeTab = 'description'">
                    <QItemSection avatar>
                        <QIcon name="description" />
                    </QItemSection>
                    <QItemSection>
                        <QItemLabel>Description</QItemLabel>
                    </QItemSection>
                </QItem>
                <QItem v-if="propertyCount !== 0 || isEditable" clickable :active="_activeTab === 'properties'" @click="_activeTab = 'properties'">
                    <QItemSection avatar>
                        <QIcon name="tune" />
                    </QItemSection>
                    <QItemSection>
                        <QItemLabel>Properties</QItemLabel>
                    </QItemSection>
                    <QItemSection side>
                        <QBadge>{{ propertyCount }}</QBadge>
                    </QItemSection>
                </QItem>
                <QItem v-if="attachmentCount === null || attachmentCount !== 0 || isEditable" clickable :active="_activeTab === 'attachments'" @click="_activeTab = 'attachments'">
                    <QItemSection avatar>
                        <QIcon name="attach_file" />
                    </QItemSection>
                    <QItemSection>
                        <QItemLabel>Attachments</QItemLabel>
                    </QItemSection>
                    <QItemSection side>
                        <QBadge>{{ attachmentCount }}</QBadge>
                    </QItemSection>
                </QItem>
                <QItem clickable :active="_activeTab === 'permissions'" @click="_activeTab = 'permissions'">
                    <QItemSection avatar>
                        <QIcon name="group" />
                    </QItemSection>
                    <QItemSection>
                        <QItemLabel>Permissions</QItemLabel>
                    </QItemSection>
                </QItem>
                <QItem v-if="isPublication" clickable :active="_activeTab === 'citation'" @click="_activeTab = 'citation'">
                    <QItemSection avatar>
                        <QIcon name="format_quote" />
                    </QItemSection>
                    <QItemSection>
                        <QItemLabel>How to cite</QItemLabel>
                    </QItemSection>
                </QItem>
            </QList>

            <!-- Action Buttons -->
            <QSeparator class="q-my-md" />
            <div class="column q-gutter-sm q-px-sm">
                <QBtn color="primary" icon="analytics" :href="`/ui/analysis-list/?subjects=${base64Subjects}`" label="Analyze" />
                <QBtn flat icon="download" :href="`${_surface.url}download/`" label="Download" />
                <QBtn v-if="!isPublication && hasFullAccess" flat icon="publish" :href="publishUrl" label="Publish" />
                <QBtn v-if="(_versions == null || _versions.length === 0) && hasFullAccess" flat icon="delete" color="negative" @click="_showDeleteModal = true" label="Delete" />
            </div>

            <!-- Version/Publication Info -->
            <template v-if="_publication != null || _surface.tags.length > 0 || _versions == null || _versions.length > 0">
                <QSeparator class="q-my-md" />
                <div class="q-px-sm">
                    <div v-if="_publication != null" class="q-mb-sm">
                        <QBadge color="info">Published by {{ _publication.publisher.name }}</QBadge>
                    </div>
                    <div v-if="_surface.tags.length > 0" class="q-mb-sm">
                        <QBadge v-for="tag in _surface.tags" :key="tag.name" color="positive" class="q-mr-xs q-mb-xs">{{ tag.name }}</QBadge>
                    </div>
                    <QBtnDropdown v-if="_versions == null || _versions.length > 0" :label="versionString" color="info" dense class="full-width">
                        <QList>
                            <QItem v-if="_publication == null || _publication.has_access_to_original_surface"
                                   clickable v-close-popup
                                   :disable="_publication == null"
                                   :href="hrefOriginalSurface">
                                <QItemSection>Work in progress</QItemSection>
                            </QItem>
                            <QItem v-if="_versions == null">
                                <QItemSection><QSpinner size="xs" /> Loading versions...</QItemSection>
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
            </template>
        </div>

        <!-- Main Content -->
        <div class="col">
            <!-- Measurements -->
            <div v-show="_activeTab === 'measurements'">
                <DropZone v-if="isEditable && !anySelected" @files-dropped="filesDropped" />
                <topography-update-card v-if="anySelected"
                                        v-model:topography="_batchEditTopography"
                                        v-model:active-tab="batchActiveTab"
                                        :batch-edit="true"
                                        :saving="_saving"
                                        @save:edit="saveBatchEdit"
                                        @discard:edit="discardBatchEdit" />
                <div v-if="isEditable && _topographies.length > 0" class="q-mb-sm q-pa-sm bg-grey-2 rounded-borders">
                    <QCheckbox v-model="allSelected" :indeterminate-value="someSelected ? null : undefined" label="Select all" size="sm" />
                </div>
                <div v-for="(topography, index) in _topographies" :key="topography?.url || index">
                    <TopographyCard v-if="topography != null"
                                    v-model:selected="_selected[index]"
                                    v-model:topography="_topographies[index]"
                                    v-model:active-tab="batchActiveTab"
                                    :disabled="!isEditable"
                                    :selectable="isEditable"
                                    :topography-url="topography.url"
                                    :syncTab="anySelected"
                                    @delete:topography="() => deleteTopography(index)" />
                </div>
            </div>

            <!-- Bandwidths -->
            <div v-show="_activeTab === 'bandwidths'">
                <div class="text-h5 q-mb-md">Bandwidths</div>
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
            </div>

            <!-- Description -->
            <div v-show="_activeTab === 'description'">
                <DatasetDescription v-if="_surface != null"
                                    :description="_surface.description"
                                    :name="_surface.name"
                                    :permission="_permissions.current_user.permission"
                                    :surface-url="_surface.url"
                                    :tags="_surface.tags" />
            </div>

            <!-- Properties -->
            <div v-show="_activeTab === 'properties'">
                <DatasetProperties v-if="_surface != null"
                                   v-model:properties="_surface.properties"
                                   :permission="_permissions.current_user.permission"
                                   :surface-url="_surface.url"
                                   v-model:propertyCount="propertyCount" />
            </div>

            <!-- Attachments -->
            <div v-show="_activeTab === 'attachments'">
                <Attachments v-if="_surface != null"
                             :attachments-url="_surface.attachments"
                             :permission="_permissions.current_user.permission"
                             v-model:attachmentCount="attachmentCount" />
            </div>

            <!-- Permissions -->
            <div v-show="_activeTab === 'permissions'">
                <DatasetPermissions v-if="_surface.publication == null"
                                    v-model:permissions="_permissions"
                                    :set-permissions-url="_surface.api.set_permissions" />
                <div v-if="_surface.publication != null">
                    <div class="text-h5 q-mb-md">Permissions</div>
                    <p>
                        This dataset is published. It is visible to everyone
                        (even without logging into the system) and can no longer be modified.
                    </p>
                </div>
            </div>

            <!-- Citation -->
            <div v-if="isPublication" v-show="_activeTab === 'citation'">
                <div class="text-h5 q-mb-md">How to cite</div>
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
            </div>
        </div>
    </div>
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
