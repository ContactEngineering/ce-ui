<script setup>

import axios from "axios";
import {computed, inject, onMounted, ref, shallowRef} from "vue";

import {
    BAccordion,
    BAccordionItem,
    BAlert,
    BCard,
    BCardText,
    BDropdown,
    BDropdownItem,
    BFormCheckbox,
    BModal,
    BSpinner,
    BTab,
    BTabs,
    BToastOrchestrator,
    useToastController
} from 'bootstrap-vue-next';

import {
    filterTopographyForPatchRequest,
    getIdFromUrl,
    subjectsToBase64
} from "../utils/api";
import {ccLicenseInfo} from "../utils/data";

import Attachments from '../manager/Attachments.vue';
import BandwidthPlot from '../manager/BandwidthPlot.vue';
import DropZone from '../components/DropZone.vue';
import DatasetDescription from '../manager/DatasetDescription.vue';
import DatasetPermissions from '../manager/DatasetPermissions.vue';
import DatasetProperties from '../manager/DatasetProperties.vue';
import TopographyCard from "../manager/TopographyCard.vue";
import TopographyUpdateCard from "../manager/TopographyUpdateCard.vue";

const {show} = useToastController();

const props = defineProps({
    surfaceUrl: {
        type: String,
        default: null
    },
    surfaceUrlPrefix: {
        type: String,
        default: '/manager/api/surface/'
    },
    newTopographyUrl: {
        type: String,
        default: '/manager/api/topography/'
    },
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

function getSurfaceUrl() {
    if (props.surfaceUrl != null) {
        return props.surfaceUrl;
    }
    const surfaceId = appProps.searchParams.get("surface");
    return `${props.surfaceUrlPrefix}${surfaceId}`;
}

const computedSurfaceUrl = computed(() => {
    return getSurfaceUrl();
});

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
    /*
    axios.get(`${getSurfaceUrl()}?children=yes&permissions=yes&attachments=yes`).then(response => {
        _surface.value = response.data;
        _permissions.value = response.data.permissions;
        _topographies.value = response.data.topography_set;
        _selected.value = new Array(_topographies.value.length).fill(false);  // Nothing is selected
        updatePublication();
    }).catch(error => {
        show?.({
            props: {
                title: "Failed to fetch digital surface twin",
                body: error,
                variant: 'danger'
            }
        });
    });
     */
    _surface.value = appProps.object;
    _permissions.value = appProps.object.permissions;
    _topographies.value = appProps.object.topography_set;
    _selected.value = new Array(_topographies.value.length).fill(false);  // Nothing is selected
    updatePublication();
}

function updatePublication() {
    if (_surface.value.publication == null) {
        _publication.value = null;
        updateVersions();
    } else {
        axios.get(_surface.value.publication).then(response => {
            _publication.value = response.data;
            updateVersions();
        }).catch(error => {
            show?.({
                props: {
                    title: "Failed to fetch publication information",
                    body: error,
                    variant: 'danger'
                }
            });
        });
    }
}

function updateVersions() {
    axios.get(`/go/api/publication/?original_surface=${getOriginalSurfaceId()}`).then(response => {
        _versions.value = response.data;
    }).catch(error => {
        show?.({
            props: {
                title: "Failed to fetch published versions",
                body: error,
                variant: 'danger'
            }
        });
    });
}

function filesDropped(files) {
    for (const file of files) {
        uploadNewTopography(file);
    }
}

function uploadNewTopography(file) {
    axios.post(props.newTopographyUrl, {
        surface: computedSurfaceUrl,
        name: file.name
    }).then(response => {
        let upload = response.data;
        upload.file = file;  // need to know which file to upload
        _topographies.value.push(upload);  // this will trigger showing a topography-upload-card
        _selected.value.push(false);  // initially unselected
    }).catch(error => {
        show?.({
            props: {
                title: "Failed to create a new measurement",
                body: error,
                variant: 'danger'
            }
        });
    });
}

function deleteTopography(index) {
    _topographies.value[index] = null;
}

function saveBatchEdit(topography) {
    // Trigger saving spinner
    _saving.value = true;

    // Clear all null fields
    const cleanedBatchEditTopography = filterTopographyForPatchRequest(topography);

    // Update all topographies and issue patch request
    for (const i in _topographies.value) {
        if (_selected.value[i]) {
            const t = {
                ..._topographies.value[i],
                ...cleanedBatchEditTopography
            }

            axios.patch(t.url, filterTopographyForPatchRequest(t)).then(response => {
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
        }
    }

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

function deleteSurface() {
    axios.delete(_surface.value.url).then(response => {
        emit('delete:surface', _surface.value.url);
        window.location.href = `/ui/dataset-list/`;
    }).catch(error => {
        show?.({
            props: {
                title: "Failed to delete digital surface twin",
                body: error,
                variant: 'danger'
            }
        });
    });
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
    return `/go/html/publish/${getSurfaceId()}/`;
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

</script>

<template>
    <BToastOrchestrator></BToastOrchestrator>
    <div class="container">
        <div v-if="_surface == null" class="d-flex justify-content-center mt-5">
            <div class="flex-column text-center">
                <b-spinner/>
                <p>Loading...</p>
            </div>
        </div>
        <div v-if="_surface != null" class="row">
            <div class="col-12">
                <BTabs class="nav-pills-custom"
                       content-class="w-100"
                       fill
                       pills
                       vertical>
                    <BTab title="Measurements">
                        <drop-zone v-if="isEditable && !anySelected"
                                   @files-dropped="filesDropped">
                        </drop-zone>
                        <topography-update-card v-if="anySelected"
                                                v-model:topography="_batchEditTopography"
                                                :batch-edit="true"
                                                :saving="_saving"
                                                @save:edit="saveBatchEdit"
                                                @discard:edit="discardBatchEdit">
                        </topography-update-card>
                        <div v-if="isEditable && _topographies.length > 0"
                             class="d-flex mb-1">
                            <BCard>
                                <BFormCheckbox v-model="allSelected"
                                               :indeterminate="someSelected" size="sm">
                                    Select all
                                </BFormCheckbox>
                            </BCard>
                        </div>
                        <div v-for="(topography, index) in _topographies">
                            <TopographyCard v-if="topography != null"
                                            v-model:selected="_selected[index]"
                                            v-model:topography="_topographies[index]"
                                            :disabled="!isEditable"
                                            :selectable="isEditable"
                                            :topography-url="topography.url"
                                            @delete:topography="() => deleteTopography(index)">
                            </TopographyCard>
                        </div>
                    </BTab>
                    <BTab title="Bandwidths">
                        <BCard class="w-100">
                            <template #header>
                                <h5 class="float-start">Bandwidths</h5>
                            </template>
                            <BAlert :model-value="_topographies.length == 0" info>
                                This surface has no measurements.
                            </BAlert>
                            <BAlert :model-value="_topographies.length > 0"
                                    secondary>
                                This bandwidth plot shows the range of length scales
                                that have been measured for
                                this digital surface twin. Each of the blocks below
                                represents one measurement.
                                Part of the bandwidth shown may be unreliable due to
                                the configured instrument's
                                measurement capacities.
                            </BAlert>
                            <bandwidth-plot v-if="_topographies.length > 0"
                                            :topographies="_topographies">
                            </bandwidth-plot>
                        </BCard>
                    </BTab>
                    <BTab title="Description">
                        <DatasetDescription v-if="_surface != null"
                                            :description="_surface.description"
                                            :name="_surface.name"
                                            :permission="_permissions.current_user.permission"
                                            :surface-url="_surface.url"
                                            :tags="_surface.tags">
                        </DatasetDescription>
                    </BTab>
                    <BTab title="Properties">
                        <DatasetProperties v-if="_surface != null"
                                           v-model:properties="_surface.properties"
                                           :permission="_permissions.current_user.permission"
                                           :surface-url="_surface.url">
                        </DatasetProperties>
                    </BTab>
                    <BTab title="Attachments">
                        <Attachments v-if="_surface != null"
                                     :attachments-url="_surface.attachments"
                                     :permission="_permissions.current_user.permission">
                        </Attachments>
                    </BTab>
                    <BTab v-if="_surface != null"
                          title="Permissions">
                        <DatasetPermissions v-if="_surface.publication == null"
                                            v-model:permissions="_permissions"
                                            :set-permissions-url="_surface.api.set_permissions">
                        </DatasetPermissions>
                        <BCard v-if="_surface.publication != null" class="w-100">
                            <template #header>
                                <h5 class="float-start">Permissions</h5>
                            </template>
                            <BCardText>
                                This dataset is published. It is visible to everyone
                                (even without logging into the
                                system) and can no longer be modified.
                            </BCardText>
                        </BCard>
                    </BTab>
                    <BTab v-if="isPublication"
                          title="How to cite">
                        <BCard class="w-100">
                            <template #header>
                                <h5 class="float-start">How to cite</h5>
                            </template>
                            <p class="mb-5">
                                <a :href="ccLicenseInfo[_publication.license].descriptionUrl">
                                    <img
                                        :src="`/static/images/cc/${_publication.license}.svg`"
                                        :title="`Dataset can be reused under the terms of the ${ccLicenseInfo[_publication.license].title}.`"
                                        style="float:right; margin-left: 0.25rem;"/>
                                </a>
                                This dataset can be reused under the terms of the
                                <a :href="ccLicenseInfo[_publication.license].descriptionUrl">
                                    {{ ccLicenseInfo[_publication.license].title }}
                                </a>.
                                When reusing this dataset, please cite the original
                                source.
                            </p>
                            <BAccordion>
                                <BAccordionItem title="Citation" visible>
                                    <div v-html="_publication.citation.html"/>
                                </BAccordionItem>
                                <BAccordionItem title="RIS">
                                    <code>
                                        <pre>{{ _publication.citation.ris }}</pre>
                                    </code>
                                </BAccordionItem>
                                <BAccordionItem title="BibTeX">
                                    <code>
                                        <pre>{{ _publication.citation.bibtex }}</pre>
                                    </code>
                                </BAccordionItem>
                                <BAccordionItem title="BibLaTeX">
                                    <code>
                                        <pre>{{ _publication.citation.biblatex }}</pre>
                                    </code>
                                </BAccordionItem>
                            </BAccordion>
                        </BCard>
                    </BTab>
                    <template #tabs-end>
                        <hr/>
                        <a :href="`/ui/analysis-list/?subjects=${base64Subjects}`"
                           class="btn btn-outline-danger mb-2 mt-2">
                            Analyze
                        </a>

                        <a :href="`${computedSurfaceUrl}download/`"
                           class="btn btn-outline-secondary mb-2">
                            Download
                        </a>

                        <a v-if="!isPublication && hasFullAccess" :href="publishUrl"
                           class="btn btn-outline-secondary mb-2">
                            Publish
                        </a>

                        <a v-if="_versions == null || _versions.length === 0 && hasFullAccess"
                           class="btn btn-outline-secondary mb-2"
                           href="#" @click="_showDeleteModal = true">
                            Delete
                        </a>
                        <hr v-if="_surface != null && (_publication != null || _surface.tags.length > 0 || _versions == null || _versions.length > 0)"/>
                        <BCard
                            v-if="_surface != null && (_publication != null || _surface.tags.length > 0 || _versions == null || _versions.length > 0)">
                            <div v-if="_publication != null">
                                <span class="badge bg-info">Published by {{
                                        _publication.publisher.name
                                    }}</span>
                            </div>
                            <div v-if="_surface.tags.length > 0">
                                <span v-for="tag in _surface.tags"
                                      class="badge bg-success">{{ tag.name }}</span>
                            </div>
                            <BDropdown
                                v-if="_versions == null || _versions.length > 0"
                                :text="versionString"
                                class="mt-2"
                                variant="info">
                                <BDropdownItem
                                    v-if="_publication == null || _publication.has_access_to_original_surface"
                                    :disabled="_publication == null"
                                    :href="hrefOriginalSurface">
                                    Work in progress
                                </BDropdownItem>
                                <BDropdownItem v-if="_versions == null">
                                    <b-spinner small/>
                                    Loading versions...
                                </BDropdownItem>
                                <BDropdownItem v-for="version in _versions"
                                               v-if="_versions != null"
                                               :disabled="_publication != null && _publication.version === version.version"
                                               :href="surfaceHrefForVersion(version)">
                                    Version {{ version.version }}
                                </BDropdownItem>
                            </BDropdown>
                        </BCard>
                    </template>
                </BTabs>
            </div>
        </div>
    </div>
    <b-modal v-if="_surface != null"
             v-model="_showDeleteModal"
             title="Delete digital surface twin"
             @ok="deleteSurface">
        You are about to delete the digital surface twin with name <b>{{
            _surface.name
        }}</b> and all contained
        measurements. Are you sure you want to proceed?
    </b-modal>
</template>
