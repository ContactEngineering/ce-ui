<script setup lang="ts">

import {cloneDeep} from "lodash";
import {computed, ref} from "vue";

import {
    QBanner,
    QBtn,
    QCard,
    QCardSection,
    QCardActions,
    QCheckbox,
    QIcon,
    QInput,
    QSelect,
    QSeparator,
    QDialog,
    QSpinner,
    QTabs,
    QTab
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
    <QCard flat bordered class="q-mb-sm"
           :class="{ 'border-negative': !batchEdit && isMetadataIncomplete, 'bg-grey-2': selected, 'bg-amber-1': batchEdit }">
        <!-- Header Row -->
        <QCardSection class="q-pa-sm">
            <div class="row items-center no-wrap">
                <!-- Left: Checkbox + Thumbnail + Name/Badges -->
                <QCheckbox v-if="selectable && !batchEdit" v-model="selectedModel"
                           :disable="_editing"
                           class="q-mr-xs" />
                <Thumbnail v-if="!batchEdit && topography != null"
                           :data-source="topography"
                           size="48px"
                           class="q-mr-sm" />
                <div v-if="!batchEdit && topography != null" class="col">
                    <div class="text-subtitle2 text-weight-medium">{{ topography.name }}</div>
                    <TopographyBadges v-if="!enlarged" :topography="topography" />
                </div>
                <div v-if="batchEdit" class="col">
                    <div class="text-subtitle1 text-weight-bold">Batch edit</div>
                    <div class="text-caption text-grey-7">Editing multiple measurements</div>
                </div>

                <!-- Right: Channel selector + Action buttons -->
                <div class="row items-center no-wrap q-gutter-xs">
                    <QSelect
                        v-if="!batchEdit && topography != null && topography.channel_names != null && topography.channel_names.length > 1"
                        :options="channelOptions"
                        v-model="topography.data_source"
                        :disable="!_editing"
                        dense outlined
                        emit-value
                        map-options
                        style="min-width: 120px;" />
                    <!-- Edit mode buttons -->
                    <template v-if="_editing || _saving || saving">
                        <QBtn v-if="_editing" flat dense color="negative" icon="close"
                              @click="discardEdits" />
                        <QBtn dense color="positive" icon="check" :loading="_saving || saving"
                              @click="saveEdits" />
                    </template>
                    <!-- Normal mode buttons -->
                    <template v-if="!batchEdit && topography != null && !_editing && !_saving && !saving">
                        <QBtn v-if="!disabled" flat dense icon="edit" :disable="selected"
                              @click="_savedTopography = cloneDeep(topography); _editing = true" />
                        <QBtn v-if="!enlarged" flat dense icon="download" :disable="selected"
                              :href="topography.datafile?.file" />
                        <QBtn v-if="!disabled" flat dense icon="refresh" :disable="selected"
                              @click="forceInspect" />
                        <QBtn v-if="!disabled && !enlarged" flat dense icon="delete" :disable="selected"
                              @click="_showDeleteModal = true" />
                        <QSeparator vertical class="q-mx-xs" />
                        <QBtn flat dense icon="analytics"
                              :href="`/ui/analysis-list/?subjects=${subjectsToBase64({topography: [topography.id]})}`" />
                        <QBtn v-if="!enlarged" flat dense icon="open_in_full" :disable="selected"
                              :href="`/ui/topography/${topography.id}/`" />
                    </template>
                </div>
            </div>
        </QCardSection>

        <!-- Loading state -->
        <QCardSection v-if="topography == null" class="q-pa-md">
            <div class="row items-center q-gutter-sm">
                <QSpinner size="1rem" />
                <span>Loading...</span>
            </div>
        </QCardSection>

        <!-- Content with Vertical Tabs -->
        <template v-if="topography != null">
            <div class="row no-wrap">
                <!-- Vertical Tabs -->
                <QTabs v-model="currentTab" vertical dense class="text-grey col-auto"
                       active-color="primary" indicator-color="primary">
                    <QTab name="home" icon="tune" />
                    <QTab name="description" icon="description" />
                    <QTab name="instrument" icon="precision_manufacturing" />
                    <QTab name="filters" icon="filter_alt" />
                    <QTab v-if="!enlarged && !batchEdit" name="attachments" icon="attach_file" />
                </QTabs>

                <QSeparator vertical />

                <!-- Tab Content -->
                <div class="col q-pa-sm">
                    <!-- Home/Properties Tab -->
                    <div v-show="currentTab === 'home'">
                        <div class="row q-col-gutter-sm">
                            <div class="col-12 col-sm-6">
                                <QInput v-model="topography.name" label="Name"
                                        :class="highlightInput('name')"
                                        :disable="!_editing || batchEdit"
                                        dense outlined />
                            </div>
                            <div class="col-6 col-sm-3">
                                <QInput type="date" v-model="topography.measurement_date" label="Date"
                                        :class="highlightInput('measurement_date')"
                                        :disable="!_editing"
                                        dense outlined />
                            </div>
                            <div class="col-6 col-sm-3">
                                <QCheckbox v-model="topography.is_periodic"
                                           :class="highlightInput('is_periodic')"
                                           :disable="!_editing || !topography.is_periodic_editable"
                                           label="Periodic" dense />
                            </div>
                        </div>
                        <div class="row q-col-gutter-sm q-mt-xs">
                            <div class="col">
                                <div class="text-caption text-grey-7 q-mb-xs">Physical size</div>
                                <div class="row items-center no-wrap q-gutter-xs">
                                    <QInput type="number" step="any" v-model="topography.size_x"
                                            :class="highlightInput('size_x')"
                                            :disable="!_editing || !topography.size_editable"
                                            dense outlined class="col" />
                                    <span v-if="batchEdit || topography.resolution_y != null">&times;</span>
                                    <QInput v-if="batchEdit || topography.resolution_y != null"
                                            type="number" step="any" v-model="topography.size_y"
                                            :class="highlightInput('size_y')"
                                            :disable="!_editing || !topography.size_editable"
                                            dense outlined class="col" />
                                    <QSelect :options="_units" v-model="topography.unit"
                                             :class="highlightInput('unit')"
                                             :disable="!_editing || !topography.unit_editable"
                                             emit-value map-options dense outlined
                                             style="width: 70px;" />
                                </div>
                            </div>
                            <div class="col-4">
                                <QInput type="number" step="any" v-model="topography.height_scale"
                                        label="Height scale"
                                        :class="highlightInput('height_scale')"
                                        :disable="!_editing || !topography.height_scale_editable"
                                        dense outlined />
                            </div>
                        </div>
                        <div v-if="batchEdit" class="text-caption text-grey-7 q-mt-sm">
                            Batch editing will only update editable entries not fixed by the data file.
                        </div>
                    </div>

                    <!-- Description Tab -->
                    <div v-show="currentTab === 'description'">
                        <TipTapEditor :disabled="!_editing" v-model="topography.description" />
                    </div>

                    <!-- Instrument Tab -->
                    <div v-show="currentTab === 'instrument'">
                        <div class="row q-col-gutter-sm">
                            <div class="col-12 col-sm-6">
                                <QInput v-model="topography.instrument_name" label="Instrument name"
                                        :class="highlightInput('instrument_name')"
                                        :disable="!_editing"
                                        dense outlined />
                            </div>
                            <div class="col-12 col-sm-6">
                                <QSelect :options="_instrumentChoices" v-model="topography.instrument_type"
                                         label="Instrument type"
                                         :class="highlightInput('instrument_type')"
                                         :disable="!_editing"
                                         emit-value map-options dense outlined />
                            </div>
                        </div>
                        <div v-if="topography.instrument_type == 'microscope-based'" class="row q-col-gutter-sm q-mt-xs">
                            <div class="col-12">
                                <div class="text-caption text-grey-7 q-mb-xs">Lateral resolution</div>
                                <div class="row items-center no-wrap q-gutter-xs">
                                    <QInput type="number" step="any"
                                            :placeholder="String(defaultResolutionValue)"
                                            :class="highlightInput('instrument_parameters')"
                                            v-model="instrumentParametersResolutionValue"
                                            :disable="!_editing"
                                            dense outlined class="col" />
                                    <QSelect :options="_units"
                                             :placeholder="defaultResolutionUnit"
                                             :class="highlightInput('instrument_parameters')"
                                             v-model="instrumentParametersResolutionUnit"
                                             :disable="!_editing"
                                             emit-value map-options dense outlined
                                             style="width: 70px;" />
                                </div>
                            </div>
                        </div>
                        <div v-if="topography.instrument_type == 'contact-based'" class="row q-col-gutter-sm q-mt-xs">
                            <div class="col-12">
                                <div class="text-caption text-grey-7 q-mb-xs">Probe tip radius</div>
                                <div class="row items-center no-wrap q-gutter-xs">
                                    <QInput type="number" step="any"
                                            :placeholder="String(defaultTipRadiusValue)"
                                            :class="highlightInput('instrument_parameters')"
                                            v-model="instrumentParametersTipRadiusValue"
                                            :disable="!_editing"
                                            dense outlined class="col" />
                                    <QSelect :options="_units"
                                             :placeholder="defaultTipRadiusUnit"
                                             :class="highlightInput('instrument_parameters')"
                                             v-model="instrumentParametersTipRadiusUnit"
                                             :disable="!_editing"
                                             emit-value map-options dense outlined
                                             style="width: 70px;" />
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Filters Tab -->
                    <div v-show="currentTab === 'filters'">
                        <div class="row q-col-gutter-sm">
                            <div class="col-12 col-sm-6">
                                <QSelect :options="_detrendChoices" v-model="topography.detrend_mode"
                                         label="Detrending"
                                         :class="highlightInput('detrend_mode')"
                                         :disable="!_editing"
                                         emit-value map-options dense outlined />
                            </div>
                            <div class="col-12 col-sm-6">
                                <QSelect :options="_undefinedDataChoices" v-model="topography.fill_undefined_data_mode"
                                         label="Undefined data"
                                         :class="highlightInput('fill_undefined_data_mode')"
                                         :disable="!_editing"
                                         emit-value map-options dense outlined />
                            </div>
                        </div>
                    </div>

                    <!-- Attachments Tab -->
                    <div v-show="!enlarged && currentTab === 'attachments'">
                        <Attachments :attachments-url="topography.attachments"
                                     :permission="topography.permissions.current_user.permission" />
                    </div>
                </div>
            </div>
        </template>
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
