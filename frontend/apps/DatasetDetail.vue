<script setup lang="ts">

import axios from "axios";
import {computed, inject, onMounted, ref, shallowRef} from "vue";

import {
    BAccordion,
    BAccordionItem,
    BAlert,
    BBadge,
    BButton,
    BCard,
    BCardText,
    BDropdown,
    BDropdownItem,
    BFormCheckbox,
    BModal,
    BSpinner,
    BTab,
    BTabs,
    useToastController
} from 'bootstrap-vue-next';

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

const {show} = useToastController();

const props = defineProps({
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
const _showBatchEditModal = ref(false);  // Triggers batch-edit modal
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
    axios.get(`/go/publication/?original_surface=${getOriginalSurfaceId()}`).then(response => {
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
        surface: _surface.value.url,
        name: file.name
    }).then(response => {
        let upload = response.data;
        upload.file = file;  // need to know which file to upload
        _topographies.value.push(upload);  // this will trigger showing a topography-upload-card
        _selected.value.push(false);  // initially unselected
    });/*.catch(error => {
        show?.({
            props: {
                title: "Failed to create a new measurement",
                body: error,
                variant: 'danger'
            }
        });
    });*/
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

    // Close the modal and stop the saving spinner
    _showBatchEditModal.value = false;
    _saving.value = false;
}

function discardBatchEdit() {
    // Reset selection
    _selected.value.fill(false);

    // Reset the batch edit topography template
    _batchEditTopography.value = emptyTopography();

    // Close the modal
    _showBatchEditModal.value = false;
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

const selectedCount = computed(() => {
    return _selected.value.reduce((x, y) => x + (y ? 1 : 0), 0);
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


</script>

<template>
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
                        <template #title>
                            Measurements <BBadge>{{measurementCount}}</BBadge>
                        </template>
                        <DropZone v-if="isEditable" @files-dropped="filesDropped">
                        </DropZone>
                        <!-- Selection toolbar: Select all, plus a Batch edit
                             button once anything is selected. -->
                        <BCard v-if="isEditable && _topographies.length > 0"
                               body-class="py-2"
                               class="mb-1">
                            <div class="d-flex align-items-center justify-content-between flex-wrap gap-2">
                                <BFormCheckbox v-model="allSelected"
                                               :indeterminate="someSelected" size="sm">
                                    Select all
                                </BFormCheckbox>
                                <div v-if="anySelected"
                                     class="d-flex align-items-center gap-2">
                                    <span class="text-secondary small">
                                        {{ selectedCount }} selected
                                    </span>
                                    <BButton variant="primary" size="sm"
                                             @click="_showBatchEditModal = true">
                                        <i class="fa fa-pen me-1"></i>Batch edit
                                    </BButton>
                                </div>
                            </div>
                        </BCard>
                        <div v-for="(topography, index) in _topographies">
                            <TopographyCard v-if="topography != null"
                                            v-model:selected="_selected[index]"
                                            v-model:topography="_topographies[index]"
                                            v-model:active-tab="batchActiveTab"
                                            :disabled="!isEditable"
                                            :selectable="isEditable"
                                            :topography-url="topography.url"
                                            :syncTab="anySelected"
                                            @delete:topography="() => deleteTopography(index)">
                            </TopographyCard>
                        </div>
                        <!-- Batch edit happens in a modal (normal colour) rather
                             than inline on top of the measurement list. The
                             Save/Discard live in the modal header, so the card
                             hides its own controls and there is no redundant
                             close button or duplicate "Batch edit" title. -->
                        <BModal v-model="_showBatchEditModal"
                                title="Batch edit"
                                size="xl"
                                no-header-close>
                            <topography-update-card v-model:topography="_batchEditTopography"
                                                    v-model:active-tab="batchActiveTab"
                                                    :batch-edit="true"
                                                    :hide-batch-controls="true"
                                                    :saving="_saving">
                            </topography-update-card>
                            <!-- Actions live in the modal footer (standard
                                 Bootstrap placement: right-aligned, primary last). -->
                            <template #footer>
                                <BButton variant="danger"
                                         @click="discardBatchEdit">
                                    Discard
                                </BButton>
                                <BButton variant="success"
                                         :disabled="_saving"
                                         @click="saveBatchEdit(_batchEditTopography)">
                                    <BSpinner small v-if="_saving"></BSpinner>
                                    Save
                                </BButton>
                            </template>
                        </BModal>
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
                    <BTab title="Properties" v-if ="propertyCount !== 0 || isEditable"> 
                        <template #title>
                            Properties <BBadge>{{ propertyCount }}</BBadge>
                        </template>
                        <DatasetProperties v-if="_surface != null"
                                           v-model:properties="_surface.properties"
                                           :permission="_permissions.current_user.permission"
                                           :surface-url="_surface.url"
                                           v-model:propertyCount="propertyCount">
                        </DatasetProperties>
                    </BTab>
                    <BTab title="Attachments" v-if ="attachmentCount === null || attachmentCount !== 0 || isEditable"> <!--here the tab will not be displayed when attachment count is 0 and is editable is false -->
                        <template #title>
                            Attachments <BBadge>{{ attachmentCount }}</BBadge>
                        </template>
                        <Attachments v-if="_surface != null" :attachments-url="_surface.attachments"
                            :permission="_permissions.current_user.permission"
                            v-model:attachmentCount="attachmentCount"
                            >
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
                            <h6>Recommended citation</h6>
                            <p>
                                When referencing this dataset or the
                                Contact.Engineering platform in a publication, we
                                recommend the following wording:
                            </p>
                            <p class="fw-semibold mb-1">
                                In the main text (software citation):
                            </p>
                            <BAlert :model-value="true" variant="secondary">
                                Portions of the topography analysis were conducted
                                using the open-source Contact.Engineering software
                                [<a href="https://doi.org/10.1088/2051-672X/ac860a"
                                    target="_blank" rel="noopener">Röttger et al.,
                                Surface Topography: Metrology and Properties 10.3
                                (2022): 035032</a>].
                            </BAlert>
                            <template v-if="_publication.doi_name">
                                <p class="fw-semibold mb-1">
                                    In the Data Availability Statement:
                                </p>
                                <BAlert :model-value="true" variant="secondary">
                                    Measured topographies have been made publicly
                                    available through Contact.Engineering
                                    [<a href="https://doi.org/10.1088/2051-672X/ac860a"
                                        target="_blank" rel="noopener">Röttger et al.,
                                    Surface Topography: Metrology and Properties 10.3
                                    (2022): 035032</a>], and are accessible via DOI:
                                    <a :href="`https://doi.org/${_publication.doi_name}`"
                                       target="_blank"
                                       rel="noopener">https://doi.org/{{ _publication.doi_name }}</a>.
                                </BAlert>
                            </template>
                            <hr/>
                            <p class="fw-semibold">
                                Bibliographic reference for this dataset:
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
                           class="btn btn-success mb-2 mt-2">
                            Analyze
                        </a>

                        <a :href="`${_surface.url}download/`"
                           class="btn btn-light mb-2">
                            Download
                        </a>

                        <a v-if="!isPublication && hasFullAccess" :href="publishUrl"
                           class="btn btn-light mb-2">
                            Publish
                        </a>

                        <a v-if="(_versions == null || _versions.length === 0) && hasFullAccess"
                           class="btn btn-danger mb-2"
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
