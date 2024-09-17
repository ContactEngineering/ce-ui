<script setup>

import axios from "axios";
import {cloneDeep} from "lodash";
import {computed, ref} from "vue";

import {
    BAlert,
    BButton,
    BButtonGroup,
    BCard,
    BCollapse,
    BFormCheckbox,
    BFormInput,
    BFormSelect,
    BFormTextarea,
    BModal,
    BSpinner
} from 'bootstrap-vue-next';

import {filterTopographyForPatchRequest, subjectsToBase64} from "../utils/api";

import TopographyBadges from "./TopographyBadges.vue";
import Attachments from './Attachments.vue';

const props = defineProps({
    batchEdit: {type: Boolean, default: false},
    defaultResolutionUnit: {type: String, default: 'nm'},
    defaultResolutionValue: {type: Number, value: 300},
    defaultTipRadiusUnit: {type: String, default: 'nm'},
    defaultTipRadiusValue: {type: Number, value: 30},
    disabled: {type: Boolean, default: false},
    enlarged: {type: Boolean, default: false},
    saving: {type: Boolean, default: false},
    selectable: {type: Boolean, default: false},
    selected: {type: Boolean, default: false},
    topography: {type: Object, default: null},
    topographyUrl: {type: String, default: null}
});

const emit = defineEmits([
    'delete:topography',
    'update:topography',
    'update:selected',
    'save:edit',
    'discard:edit'
]);

const selectedModel = computed({
    get() {
        return props.selected;
    },
    set(value) {
        emit('update:selected', value);
    }
});

// Switches controlling visibility
const _descriptionVisible = ref(props.enlarged);
const _filtersVisible = ref(props.enlarged);
const _instrumentVisible = ref(props.enlarged);
const _attachmentsVisible = ref(props.enlarged);

// GUI logic
const _editing = ref(props.batchEdit);
const _error = ref(null);
const _saving = ref(false);
const _showDeleteModal = ref(false);

// Old topography data (used to restore data when "Discard" is clicked)
let _savedTopography = null;

// Choices for select form components
const _units = [
    {value: "km", text: 'km'},
    {value: "m", text: 'm'},
    {value: "mm", text: 'mm'},
    {value: "µm", text: 'µm'},
    {value: "nm", text: 'nm'},
    {value: "Å", text: 'Å'},
    {value: "pm", text: 'pm'}
];
const _instrumentChoices = [
    {
        value: 'undefined',
        text: 'Instrument of unknown type - all data considered as reliable'
    },
    {
        value: 'microscope-based',
        text: 'Microscope-based instrument with known resolution'
    },
    {value: 'contact-based', text: 'Contact-based instrument with known tip radius'}
];
const _detrendChoices = [
    {value: 'center', text: 'No detrending, but subtract mean height'},
    {value: 'height', text: 'Remove tilt'},
    {value: 'curvature', text: 'Remove curvature and tilt'}
];
const _undefinedDataChoices = [
    {value: 'do-not-fill', text: 'Do not fill undefined data points'},
    {
        value: 'harmonic',
        text: 'Interpolate undefined data points with harmonic functions'
    }
];

function saveEdits() {
    if (props.batchEdit) {
        emit('save:edit', props.topography);
    } else {
        _editing.value = false;
        _saving.value = true;
        axios.patch(props.topographyUrl, filterTopographyForPatchRequest(props.topography)).then(response => {
            _error.value = null;
            emit('update:topography', response.data);
        }).catch(error => {
            _error.value = error;
            emit('update:topography', _savedTopography);
        }).finally(() => {
            _saving.value = false;
        });
    }
}

function discardEdits() {
    if (props.batchEdit) {
        // Tell upstream components that discard was click
        emit('discard:edit');
    } else {
        // Turn off editing and restore prior state
        _editing.value = false;
        emit('update:topography', _savedTopography);
    }
}

function deleteTopography() {
    axios.delete(props.topographyUrl).then(response => {
        emit('delete:topography', props.topographyUrl);
    }).catch(error => {
        _error.value = error;
    });
}

function forceInspect() {
    axios.post(`${props.topographyUrl}force-inspect/`).then(response => {
        emit('update:topography', response.data);
    }).catch(error => {
        _error.value = error;
    });
}

const isMetadataIncomplete = computed(() => {
    if (props.topography != null && props.topography.is_metadata_complete !== undefined) {
        return !props.topography.is_metadata_complete;
    } else {
        return true;
    }
});

const channelOptions = computed(() => {
    if (props.topography == null) {
        return [];
    }

    let options = [];
    for (const [channelIndex, channelName] of props.topography.channel_names.entries()) {
        const [name, unit] = channelName;
        if (unit == null) {
            options.push({value: channelIndex, text: name});
        } else {
            options.push({value: channelIndex, text: `${name} (${unit})`});
        }
    }
    return options;
});

// Select class for highlighting input fields. Field are highlighted
// * danger/red if they are necessary for metadata to be complete
// * success/green if they have value during batch editing, i.e. if that value will be updated for all selected
//   topographies
function highlightInput(key) {
    let highlightMandatoryInput = {};
    if (['size_x', 'size_y', 'unit', 'height_scale'].includes(key)) {
        highlightMandatoryInput = {'bg-danger-subtle': !props.batchEdit && props.topography[key] == null};
    }
    return {
        ...highlightMandatoryInput,
        'bg-success-subtle': props.batchEdit
            && props.topography[key] != null
            && (props.topography[key].length === undefined || props.topography[key].length > 0)  // tags cannot be null
    };
}

// Transform instrument parameters to a model
function instrumentParameterModel(key1, key2) {
    return computed({
        get() {
            if (props.topography.instrument_parameters != null) {
                if (props.topography.instrument_parameters[key1] != null) {
                    return props.topography.instrument_parameters[key1][key2];
                }
            }
            return null;
        },
        set(v) {
            let t = cloneDeep(props.topography);
            if (t.instrument_parameters == null) {
                t.instrument_parameters = {[key1]: {[key2]: v}};
            } else if (t.instrument_parameters[key1] == null) {
                t.instrument_parameters[key1] = {[key2]: v};
            } else {
                t.instrument_parameters[key1][key2] = v;
            }
            emit('update:topography', t);
        }
    });
}

const instrumentParametersResolutionValue = instrumentParameterModel('resolution', 'value');
const instrumentParametersResolutionUnit = instrumentParameterModel('resolution', 'unit');
const instrumentParametersTipRadiusValue = instrumentParameterModel('tip_radius', 'value');
const instrumentParametersTipRadiusUnit = instrumentParameterModel('tip_radius', 'unit');

const hasThumbnail = computed(() => props.topography.thumbnail != null && props.topography.thumbnail.file != null);

</script>

<template>
    <BCard class="mb-1"
           :class="{ 'border-danger border-2': !batchEdit && isMetadataIncomplete, 'bg-secondary-subtle': selected, 'bg-warning-subtle': batchEdit }">
        <template #header>
            <div v-if="!batchEdit && topography != null" class="d-flex float-start">
                <BFormCheckbox v-if="selectable" v-model="selectedModel"
                               :disabled="_editing"
                               size="sm">
                </BFormCheckbox>
                <BFormSelect
                    v-if="topography.channel_names != null && topography.channel_names.length > 0"
                    :options="channelOptions"
                    v-model="topography.data_source"
                    :disabled="!_editing"
                    size="sm">
                </BFormSelect>
            </div>
            <div v-if="batchEdit" class="float-start fs-5 fw-bold">
                Batch edit
            </div>
            <BButtonGroup
                v-if="!batchEdit && topography != null && !_editing && !_saving && !saving && !enlarged"
                size="sm" class="float-end">
                <BButton v-if="!selected"
                         class="float-end ms-2"
                         variant="outline-secondary"
                         :href="`/ui/html/topography/?topography=${topography.id}`">
                    <i class="fa fa-expand"></i>
                </BButton>
                <BButton v-if="selected"
                         class="float-end ms-2"
                         variant="outline-secondary"
                         disabled>
                    <i class="fa fa-expand"></i>
                </BButton>
            </BButtonGroup>
            <BButtonGroup
                v-if="!batchEdit && topography != null && !_editing && !_saving && !saving"
                size="sm" class="float-end">
                <BButton v-if="!disabled"
                         variant="outline-secondary"
                         :disabled="selected"
                         @click="_savedTopography = cloneDeep(topography); _editing = true">
                    <i class="fa fa-pen"></i>
                </BButton>
                <BButton v-if="!enlarged && !selected"
                         variant="outline-secondary"
                         :href="topography.datafile">
                    <i class="fa fa-download"></i>
                </BButton>
                <BButton v-if="!disabled && selected"
                         variant="outline-secondary"
                         disabled>
                    <i class="fa fa-download"></i>
                </BButton>
                <BButton v-if="!disabled"
                         variant="outline-secondary"
                         :disabled="selected">
                    <i class="fa fa-refresh"
                       @click="forceInspect"></i>
                </BButton>
                <BButton v-if="!disabled && !enlarged"
                         :disabled="selected"
                         variant="outline-secondary"
                         @click="_showDeleteModal = true">
                    <i class="fa fa-trash"></i>
                </BButton>
            </BButtonGroup>
            <BButtonGroup v-if="_editing || _saving || saving" size="sm"
                          class="float-end">
                <BButton v-if="_editing"
                         variant="danger"
                         @click="discardEdits">
                    Discard
                </BButton>
                <BButton variant="success"
                         @click="saveEdits">
                    <BSpinner small v-if="_saving || saving"></BSpinner>
                    Save
                </BButton>
            </BButtonGroup>
            <BButtonGroup v-if="!batchEdit" size="sm" class="float-end me-2">
                <BButton variant="outline-secondary"
                         :href="`/ui/html/analysis-list/?subjects=${subjectsToBase64({topography: [topography.id]})}`">
                    Analyze
                </BButton>
            </BButtonGroup>
            <BButtonGroup size="sm" class="float-end me-2">
                <BButton v-if="!enlarged"
                         v-model:pressed="_descriptionVisible"
                         variant="outline-secondary">
                    Description
                </BButton>
                <BButton v-if="!enlarged"
                         v-model:pressed="_instrumentVisible"
                         variant="outline-secondary">
                    Instrument
                </BButton>
                <BButton v-if="!enlarged"
                         v-model:pressed="_filtersVisible"
                         variant="outline-secondary">
                    Filters
                </BButton>
                <BButton v-if="!enlarged"
                         v-model:pressed="_attachmentsVisible"
                         variant="outline-secondary">
                    Attachments
                </BButton>
            </BButtonGroup>
        </template>
        <BAlert :model-value="_error != null" variant="danger">
            {{ _error.message }}
        </BAlert>
        <div v-if="topography == null" class="tab-content">
            <BSpinner small></BSpinner>
            Please wait...
        </div>
        <div v-if="topography != null" class="row">
            <div v-if="hasThumbnail" class="col-2">
                <a :href="`/ui/html/topography/?topography=${topography.id}`">
                    <img class="img-thumbnail mw-100"
                         :src="topography.thumbnail.file">
                </a>
            </div>
            <div
                :class="{ 'col-10': hasThumbnail, 'col-12': hasThumbnail }">
                <div class="container">
                    <div class="row">
                        <div class="col-6">
                            <label for="input-name">Name</label>
                            <BFormInput id="input-name"
                                        v-model="topography.name"
                                        :class="highlightInput('name')"
                                        :disabled="!_editing || batchEdit">
                            </BFormInput>
                        </div>
                        <div class="col-3">
                            <label for="input-measurement-date">Date</label>
                            <BFormInput id="input-measurement-date"
                                        type="date"
                                        v-model="topography.measurement_date"
                                        :class="highlightInput('measurement_date')"
                                        :disabled="!_editing">
                            </BFormInput>
                        </div>
                        <div class="col-3">
                            <label for="input-periodic">Flags</label>
                            <BFormCheckbox id="input-periodic"
                                           v-model="topography.is_periodic"
                                           :class="highlightInput('is_periodic')"
                                           :disabled="!_editing || !topography.is_periodic_editable">
                                Data is periodic
                            </BFormCheckbox>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-8">
                            <label for="input-physical-size">Physical size</label>
                            <div class="input-group mb-1">
                                <BFormInput id="input-physical-size"
                                            type="number"
                                            step="any"
                                            :class="highlightInput('size_x')"
                                            v-model="topography.size_x"
                                            :disabled="!_editing || !topography.size_editable">
                                </BFormInput>
                                <span
                                    v-if="batchEdit || topography.resolution_y != null"
                                    class="input-group-text">
                                            &times;
                                        </span>
                                <BFormInput
                                    v-if="batchEdit || topography.resolution_y != null"
                                    type="number"
                                    step="any"
                                    :class="highlightInput('size_y')"
                                    v-model="topography.size_y"
                                    :disabled="!_editing || !topography.size_editable">
                                </BFormInput>
                                <BFormSelect class="unit-select"
                                             :options="_units"
                                             v-model="topography.unit"
                                             :class="highlightInput('unit')"
                                             :disabled="!_editing || !topography.unit_editable">
                                </BFormSelect>
                            </div>
                            <small v-if="batchEdit">
                                When batch editing line scans, only the first entry of
                                the physical size
                                will be used to set the overall length of the line scan.
                            </small>
                        </div>
                        <div class="col-4">
                            <label for="input-physical-size">Height scale</label>
                            <BFormInput id="input-physical-size"
                                        type="number"
                                        step="any"
                                        :class="highlightInput('height_scale')"
                                        v-model="topography.height_scale"
                                        :disabled="!_editing || !topography.height_scale_editable">
                            </BFormInput>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div v-if="_descriptionVisible">
            <label for="input-description">Description</label>
            <BFormTextarea id="input-description"
                           placeholder="Please provide a short description of this measurement"
                           v-model="topography.description"
                           :class="highlightInput('description')"
                           :disabled="!_editing"
                           rows="5">
            </BFormTextarea>
        </div>
        <div v-if="_instrumentVisible">
            <div class="row">
                <div class="col-6">
                    <label for="input-instrument-name">Instrument name</label>
                    <BFormInput id="input-instrument-name"
                                :class="highlightInput('instrument_name')"
                                v-model="topography.instrument_name"
                                :disabled="!_editing">
                    </BFormInput>
                </div>
                <div class="col-6">
                    <label for="input-instrument-type">Instrument type</label>
                    <BFormSelect id="input-instrument-type"
                                 :options="_instrumentChoices"
                                 :class="highlightInput('instrument_type')"
                                 v-model="topography.instrument_type"
                                 :disabled="!_editing">
                    </BFormSelect>
                </div>
            </div>
            <div v-if="topography.instrument_type == 'microscope-based'" class="row">
                <div class="col-12 mt-1">
                    <label for="input-instrument-resolution">Lateral instrument
                        resolution</label>
                    <div id="input-instrument-resolution" class="input-group mb-1">
                        <BFormInput type="number"
                                    step="any"
                                    :placeholder="defaultResolutionValue"
                                    :class="highlightInput('instrument_parameters')"
                                    v-model="instrumentParametersResolutionValue"
                                    :disabled="!_editing">
                        </BFormInput>
                        <BFormSelect style="width: 100px;"
                                     :options="_units"
                                     :placeholder="defaultResolutionUnit"
                                     :class="highlightInput('instrument_parameters')"
                                     v-model="instrumentParametersResolutionUnit"
                                     :disabled="!_editing">
                        </BFormSelect>
                    </div>
                </div>
            </div>
            <div v-if="topography.instrument_type == 'contact-based'" class="row">
                <div class="col-12 mt-1">
                    <label for="input-instrument-tip-radius">Probe tip radius</label>
                    <div id="input-instrument-tip-radius" class="input-group mb-1">
                        <BFormInput type="number"
                                    step="any"
                                    :placeholder="defaultTipRadiusValue"
                                    :class="highlightInput('instrument_parameters')"
                                    v-model="instrumentParametersTipRadiusValue"
                                    :disabled="!_editing">
                        </BFormInput>
                        <BFormSelect style="width: 100px;"
                                     :options="_units"
                                     :placeholder="defaultTipRadiusUnit"
                                     :class="highlightInput('instrument_parameters')"
                                     v-model="instrumentParametersTipRadiusUnit"
                                     :disabled="!_editing">
                        </BFormSelect>
                    </div>
                </div>
            </div>
        </div>
        <div v-if="_filtersVisible">
            <div class="row">
                <div class="col-6 mt-1">
                    <label for="input-detrending">Detrending</label>
                    <div id="input-detrending" class="input-group mb-1">
                        <BFormSelect :options="_detrendChoices"
                                     v-model="topography.detrend_mode"
                                     :class="highlightInput('detrend_mode')"
                                     :disabled="!_editing">
                        </BFormSelect>
                    </div>
                </div>
                <div class="col-6 mt-1">
                    <label for="input-undefined-data">Undefined/missing data</label>
                    <div id="input-undefined-data" class="input-group mb-1">
                        <BFormSelect :options="_undefinedDataChoices"
                                     v-model="topography.fill_undefined_data_mode"
                                     :class="highlightInput('fill_undefined_data_mode')"
                                     :disabled="!_editing">
                        </BFormSelect>
                    </div>
                </div>
            </div>
        </div>
        <div v-if="_attachmentsVisible" class="container">
            <attachments :file-parent-type="'topography'"
                         :file-parent-url="topography.url"
                         :attachments="topography.attachments"
                         :permission="topography.permissions.current_user.permission">
            </attachments>
        </div>
        <template #footer>
            <TopographyBadges v-if="!batchEdit && !enlarged"
                              :topography="topography"></TopographyBadges>
            <small v-if="batchEdit">You are about to change the metadata of multiple
                measurements. Note that batch
                editing will only
                update entries that are editable, i.e. that are not fixed by the
                contents of the data file. This
                includes physical sizes, unit or the height scale and may differ between
                the measurements you are
                updating.</small>
        </template>
    </BCard>
    <BModal v-if="topography != null"
            v-model="_showDeleteModal"
            @ok="deleteTopography"
            title="Delete measurement">
        You are about to delete the measurement with name <b>{{ topography.name }}</b>.
        Are you sure you want to proceed?
    </BModal>
</template>
