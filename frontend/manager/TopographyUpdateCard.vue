<script setup lang="ts">

import {cloneDeep} from "lodash";
import {computed, ref} from "vue";

import {
    QBanner,
    QBtn,
    QBtnGroup,
    QCard,
    QCardSection,
    QCheckbox,
    QInput,
    QSelect,
    QDialog,
    QSpinner
} from 'quasar';

import { useNotify } from "@/utils/notify";

import {
    managerApiTopographyPartialUpdate,
    managerApiTopographyDestroy,
    managerApiTopographyForceInspectCreate
} from "@/api";

import {filterTopographyForPatchRequest, getIdFromUrl, subjectsToBase64} from "../utils/api";

import TopographyBadges from "./TopographyBadges.vue";
import Attachments from './Attachments.vue';
import Thumbnail from "./Thumbnail.vue";
import TipTapEditor from "./TipTapEditor.vue";

const { show } = useNotify();

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
    topographyUrl: {type: String, default: null},
    syncTab: { type: Boolean, default: false }
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
const activeTab = defineModel('activeTab', {
    type: String,
    default: 'home'
});

function handlebatchTabChange(value) {  
    activeTab.value = value;
}

const localTab = ref('home');

const currentTab = computed({
  get() {
    return props.batchEdit||props.syncTab ? activeTab.value : localTab.value; 
  },
  set(value) {
    if (props.batchEdit||props.syncTab) {
      handlebatchTabChange(value);
    } else {
      localTab.value = value;
    }
  },
});



// GUI logic
const _editing = ref(props.batchEdit);
const _saving = ref(false);
const _showDeleteModal = ref(false);

// Old topography data (used to restore data when "Discard" is clicked)
let _savedTopography = null;

// Choices for select form components
const _units = [
    {value: "km", label: 'km'},
    {value: "m", label: 'm'},
    {value: "mm", label: 'mm'},
    {value: "µm", label: 'µm'},
    {value: "nm", label: 'nm'},
    {value: "Å", label: 'Å'},
    {value: "pm", label: 'pm'}
];
const _instrumentChoices = [
    {
        value: 'undefined',
        label: 'Instrument of unknown type - all data considered as reliable'
    },
    {
        value: 'microscope-based',
        label: 'Microscope-based instrument with known resolution'
    },
    {value: 'contact-based', label: 'Contact-based instrument with known tip radius'}
];
const _detrendChoices = [
    {value: 'center', label: 'No detrending, but subtract mean height'},
    {value: 'height', label: 'Remove tilt'},
    {value: 'curvature', label: 'Remove curvature and tilt'}
];
const _undefinedDataChoices = [
    {value: 'do-not-fill', label: 'Do not fill undefined data points'},
    {
        value: 'harmonic',
        label: 'Interpolate undefined data points with harmonic functions'
    }
];

async function saveEdits() {
    if (props.batchEdit) {
        emit('save:edit', props.topography);
    } else {
        _editing.value = false;
        _saving.value = true;
        try {
            const topographyId = getIdFromUrl(props.topographyUrl);
            const response = await managerApiTopographyPartialUpdate({
                path: {id: topographyId},
                body: filterTopographyForPatchRequest(props.topography)
            });
            emit('update:topography', response.data);
        } catch (error) {
            show?.({
                title: "Failed to save changes",
                body: error,
                variant: 'danger'
            });
            emit('update:topography', _savedTopography);
        } finally {
            _saving.value = false;
        }
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

async function deleteTopography() {
    try {
        const topographyId = getIdFromUrl(props.topographyUrl);
        await managerApiTopographyDestroy({path: {id: topographyId}});
        emit('delete:topography', props.topographyUrl);
    } catch (error) {
        show?.({
            title: "Failed to delete measurement",
            body: error,
            variant: 'danger'
        });
    }
}

async function forceInspect() {
    try {
        const topographyId = getIdFromUrl(props.topographyUrl);
        const response = await managerApiTopographyForceInspectCreate({path: {id: topographyId}});
        emit('update:topography', response.data);
    } catch (error) {
        show?.({
            title: "Failed to force file inspection",
            body: error,
            variant: 'danger'
        });
    }
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

        const options = props.topography.channel_names.map(([name, unit], channelIndex) => {
            return {
                value: channelIndex,
                label: unit == null ? name : `${name} (${unit})`
            };
        });

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

</script>

<template>
    <QCard class="q-mb-xs"
           :class="{ 'border-negative': !batchEdit && isMetadataIncomplete, 'bg-grey-3': selected, 'bg-warning-1': batchEdit }">
        <QCardSection class="flex items-center q-pa-sm">
            <div v-if="!batchEdit && topography != null" class="flex items-center">
                <QCheckbox v-if="selectable" v-model="selectedModel"
                           :disable="_editing"
                           size="sm" />
                <QSelect
                    v-if="topography.channel_names != null && topography.channel_names.length > 0"
                    :options="channelOptions"
                    v-model="topography.data_source"
                    :disable="!_editing"
                    dense
                    emit-value
                    map-options
                    size="sm"
                    style="min-width: 120px;" />
            </div>
            <div v-if="batchEdit" class="text-subtitle1 text-weight-bold">
                Batch edit
            </div>
            <div class="col-grow"></div>
            <QBtnGroup flat class="q-mr-sm">
                <QBtn :flat="currentTab !== 'home'"
                      :outline="currentTab === 'home'"
                      @click="currentTab = 'home'"
                      size="sm"
                      label="Home" />

                <QBtn :flat="currentTab !== 'description'"
                      :outline="currentTab === 'description'"
                      @click="currentTab = 'description'"
                      size="sm"
                      label="Description" />

                <QBtn :flat="currentTab !== 'instrument'"
                      :outline="currentTab === 'instrument'"
                      @click="currentTab = 'instrument'"
                      size="sm"
                      label="Instrument" />

                <QBtn :flat="currentTab !== 'filters'"
                      :outline="currentTab === 'filters'"
                      @click="currentTab = 'filters'"
                      size="sm"
                      label="Filters" />

                <QBtn v-if="!enlarged && !batchEdit"
                      :flat="currentTab !== 'attachments'"
                      :outline="currentTab === 'attachments'"
                      @click="currentTab = 'attachments'"
                      size="sm"
                      label="Attachments" />
            </QBtnGroup>
            <QBtnGroup v-if="!batchEdit" flat class="q-mr-sm">
                <QBtn flat size="sm"
                      :href="`/ui/analysis-list/?subjects=${subjectsToBase64({topography: [topography.id]})}`"
                      label="Analyze" />
            </QBtnGroup>
            <QBtnGroup v-if="_editing || _saving || saving" flat>
                <QBtn v-if="_editing"
                      color="negative" size="sm"
                      @click="discardEdits"
                      label="Discard" />
                <QBtn color="positive" size="sm"
                      @click="saveEdits">
                    <QSpinner v-if="_saving || saving" size="1rem" class="q-mr-sm" />
                    Save
                </QBtn>
            </QBtnGroup>
            <QBtnGroup
                v-if="!batchEdit && topography != null && !_editing && !_saving && !saving"
                flat>
                <QBtn v-if="!disabled"
                      flat size="sm" icon="edit"
                      :disable="selected"
                      @click="_savedTopography = cloneDeep(topography); _editing = true" />
                <QBtn v-if="!enlarged && !selected"
                      flat size="sm" icon="download"
                      :href="topography.datafile?.file" />
                <QBtn v-if="!disabled && selected"
                      flat size="sm" icon="download"
                      disable />
                <QBtn v-if="!disabled"
                      flat size="sm" icon="refresh"
                      :disable="selected"
                      @click="forceInspect" />
                <QBtn v-if="!disabled && !enlarged"
                      :disable="selected"
                      flat size="sm" icon="delete"
                      @click="_showDeleteModal = true" />
            </QBtnGroup>
            <QBtnGroup
                v-if="!batchEdit && topography != null && !_editing && !_saving && !saving && !enlarged"
                flat class="q-ml-sm">
                <QBtn v-if="!selected"
                      flat size="sm" icon="fullscreen"
                      :href="`/ui/topography/${topography.id}/`" />
                <QBtn v-if="selected"
                      flat size="sm" icon="fullscreen"
                      disable />
            </QBtnGroup>
        </QCardSection>
        <QCardSection v-if="topography == null">
            <QSpinner size="1rem" class="q-mr-sm" />
            Please wait...
        </QCardSection>
        <QCardSection v-if="topography != null" class="row">
            <div class="col-2">
                <Thumbnail img-class="img-thumbnail"
                           :data-source="topography">
                </Thumbnail>
            </div>
            <div v-if="currentTab === 'home'" class="col-10">
                <div class="row">
                    <div class="col-6">
                        <label for="input-name">Name</label>
                        <QInput id="input-name"
                                v-model="topography.name"
                                :class="highlightInput('name')"
                                :disable="!_editing || batchEdit"
                                dense outlined />
                    </div>
                    <div class="col-3">
                        <label for="input-measurement-date">Date</label>
                        <QInput id="input-measurement-date"
                                type="date"
                                v-model="topography.measurement_date"
                                :class="highlightInput('measurement_date')"
                                :disable="!_editing"
                                dense outlined />
                    </div>
                    <div class="col-3">
                        <label for="input-periodic">Flags</label>
                        <QCheckbox id="input-periodic"
                                   v-model="topography.is_periodic"
                                   :class="highlightInput('is_periodic')"
                                   :disable="!_editing || !topography.is_periodic_editable"
                                   label="Data is periodic" />
                    </div>
                </div>
                <div class="row">
                    <div class="col-8">
                        <label for="input-physical-size">Physical size</label>
                        <div class="flex q-mb-xs">
                            <QInput id="input-physical-size"
                                    type="number"
                                    step="any"
                                    :class="highlightInput('size_x')"
                                    v-model="topography.size_x"
                                    :disable="!_editing || !topography.size_editable"
                                    dense outlined
                                    class="col-grow" />
                            <span
                                v-if="batchEdit || topography.resolution_y != null"
                                class="q-px-sm self-center">
                                        &times;
                                    </span>
                            <QInput
                                v-if="batchEdit || topography.resolution_y != null"
                                type="number"
                                step="any"
                                :class="highlightInput('size_y')"
                                v-model="topography.size_y"
                                :disable="!_editing || !topography.size_editable"
                                dense outlined
                                class="col-grow" />
                            <QSelect class="unit-select q-ml-sm"
                                     :options="_units"
                                     v-model="topography.unit"
                                     :class="highlightInput('unit')"
                                     :disable="!_editing || !topography.unit_editable"
                                     emit-value
                                     map-options
                                     dense outlined
                                     style="min-width: 80px;" />
                        </div>
                        <small v-if="batchEdit">
                            When batch editing line scans, only the first entry of
                            the physical size
                            will be used to set the overall length of the line scan.
                        </small>
                    </div>
                    <div class="col-4">
                        <label for="input-height-scale">Height scale</label>
                        <QInput id="input-height-scale"
                                type="number"
                                step="any"
                                :class="highlightInput('height_scale')"
                                v-model="topography.height_scale"
                                :disable="!_editing || !topography.height_scale_editable"
                                dense outlined />
                    </div>
                </div>
            </div>
            <div v-if="currentTab === 'description'" class="col-10">
                <label for="input-description">Description</label>
                <TipTapEditor :disabled="!_editing" v-model="topography.description" />
            </div>
            <div v-if="currentTab === 'instrument'" class="col-10">
                <div class="row">
                    <div class="col-6">
                        <label for="input-instrument-name">Instrument name</label>
                        <QInput id="input-instrument-name"
                                :class="highlightInput('instrument_name')"
                                v-model="topography.instrument_name"
                                :disable="!_editing"
                                dense outlined />
                    </div>
                    <div class="col-6">
                        <label for="input-instrument-type">Instrument type</label>
                        <QSelect id="input-instrument-type"
                                 :options="_instrumentChoices"
                                 :class="highlightInput('instrument_type')"
                                 v-model="topography.instrument_type"
                                 :disable="!_editing"
                                 emit-value
                                 map-options
                                 dense outlined />
                    </div>
                </div>
                <div v-if="topography.instrument_type == 'microscope-based'" class="row">
                    <div class="col-12 q-mt-xs">
                        <label for="input-instrument-resolution">Lateral instrument
                            resolution</label>
                        <div class="flex q-mb-xs">
                            <QInput type="number"
                                    step="any"
                                    :placeholder="String(defaultResolutionValue)"
                                    :class="highlightInput('instrument_parameters')"
                                    v-model="instrumentParametersResolutionValue"
                                    :disable="!_editing"
                                    dense outlined
                                    class="col-grow" />
                            <QSelect style="width: 100px;"
                                     :options="_units"
                                     :placeholder="defaultResolutionUnit"
                                     :class="highlightInput('instrument_parameters')"
                                     v-model="instrumentParametersResolutionUnit"
                                     :disable="!_editing"
                                     emit-value
                                     map-options
                                     dense outlined />
                        </div>
                    </div>
                </div>
                <div v-if="topography.instrument_type == 'contact-based'" class="row">
                    <div class="col-12 q-mt-xs">
                        <label for="input-instrument-tip-radius">Probe tip radius</label>
                        <div class="flex q-mb-xs">
                            <QInput type="number"
                                    step="any"
                                    :placeholder="String(defaultTipRadiusValue)"
                                    :class="highlightInput('instrument_parameters')"
                                    v-model="instrumentParametersTipRadiusValue"
                                    :disable="!_editing"
                                    dense outlined
                                    class="col-grow" />
                            <QSelect style="width: 100px;"
                                     :options="_units"
                                     :placeholder="defaultTipRadiusUnit"
                                     :class="highlightInput('instrument_parameters')"
                                     v-model="instrumentParametersTipRadiusUnit"
                                     :disable="!_editing"
                                     emit-value
                                     map-options
                                     dense outlined />
                        </div>
                    </div>
                </div>
            </div>
            <div v-if="currentTab === 'filters'" class="col-10">
                <div class="row">
                    <div class="col-6 q-mt-xs">
                        <label for="input-detrending">Detrending</label>
                        <QSelect :options="_detrendChoices"
                                 v-model="topography.detrend_mode"
                                 :class="highlightInput('detrend_mode')"
                                 :disable="!_editing"
                                 emit-value
                                 map-options
                                 dense outlined />
                    </div>
                    <div class="col-6 q-mt-xs">
                        <label for="input-undefined-data">Undefined/missing data</label>
                        <QSelect :options="_undefinedDataChoices"
                                 v-model="topography.fill_undefined_data_mode"
                                 :class="highlightInput('fill_undefined_data_mode')"
                                 :disable="!_editing"
                                 emit-value
                                 map-options
                                 dense outlined />
                    </div>
                </div>
            </div>
            <div v-if="!enlarged && currentTab === 'attachments'" class="col-10">
                <Attachments :attachments-url="topography.attachments"
                            :permission="topography.permissions.current_user.permission">
                </Attachments>
            </div>
        </QCardSection>
        <QCardSection v-if="topography != null">
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
        </QCardSection>
    </QCard>
    <QDialog v-model="_showDeleteModal">
        <QCard v-if="topography != null" style="min-width: 350px">
            <QCardSection class="row items-center">
                <div class="text-h6">Delete measurement</div>
            </QCardSection>
            <QCardSection>
                You are about to delete the measurement with name <b>{{ topography.name }}</b>.
                Are you sure you want to proceed?
            </QCardSection>
            <QCardSection class="flex justify-end q-gutter-sm">
                <QBtn flat label="Cancel" v-close-popup />
                <QBtn color="negative" label="Delete" @click="deleteTopography" v-close-popup />
            </QCardSection>
        </QCard>
    </QDialog>
</template>
