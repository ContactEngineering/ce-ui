<script setup>

import {ref} from "vue";

import {
    BForm,
    BFormCheckbox,
    BFormInput,
    BFormRadio,
    BFormSelect,
    BFormSelectOption,
    BFormTags,
    BInputGroup,
    BInputGroupText,
    BModal
} from "bootstrap-vue-next";

const visible = defineModel('visible', {required: true});
const kwargs = defineModel('kwargs', {required: true});

const emit = defineEmits(['updateKwargs']);

const props = defineProps({
    limitsToFunctionKwargs: Object,
});

const _enableHardness = ref(kwargs.value === undefined ? false : kwargs.value.hardness !== null);
const _hardness = ref(kwargs.value === undefined ? null : kwargs.value.hardness);
const _maxNbIter = ref(kwargs.value === undefined ? 100 : kwargs.value.maxiter);
const _nbSteps = ref(kwargs.value === undefined ? 10 : kwargs.value.nsteps);
const _periodicity = ref(kwargs.value === undefined ? "nonperiodic" : kwargs.value.substrate);
const _periodicityOptions = ref([
    {value: "periodic", text: "Periodic (repeating array of the measurement)"},
    {value: "nonperiodic", text: "Free boundaries (flat punch with measurement)"}
]);
const _pressureSelection = ref(kwargs.value == null ? "automatic" :
    (kwargs.value.pressures == null ? "automatic" : "manual"));
const _pressures = ref(kwargs.value == null ? [] :
    (kwargs.value.pressures == null ? [] : kwargs.value.pressures));
const _recalculateWarning = ref(false);

function validateParameters(event) {
    let pressures = null;
    _recalculateWarning.value = false;

    if (_enableHardness.value) {
        if (_hardness.value < 0) {
            _hardness.value = 0;
            _recalculateWarning.value = true;
        }
    }

    if (_pressureSelection.value === "automatic") {
        if (_nbSteps.value < props.limitsToFunctionKwargs.nsteps.min) {
            _nbSteps.value = props.limitsToFunctionKwargs.nsteps.min;
            _recalculateWarning.value = true;
        }
        if (_nbSteps > props.limitsToFunctionKwargs.nsteps.max) {
            _nbSteps.value = props.limitsToFunctionKwargs.nsteps.max;
            _recalculateWarning.value = true;
        }
    } else { // pressure_selection_mode == "manual"
        if (_pressures.value == null) {
            pressures = [1];
        } else {
            pressures = _pressures.value.map(parseFloat).filter(p => {
                return (p != null) && (p > 0)
            }).sort();
        }
        if (pressures.length < 1) {
            pressures = [1];
        } else if (pressures.length > props.limitsToFunctionKwargs.pressures.maxlen) {
            pressures.length = props.limitsToFunctionKwargs.pressures.maxlen;
        }
        if (String(pressures) !== String(_pressures.value)) {
            _recalculateWarning.value = true;
        }
        _pressures.value = pressures;
    }

    if (_maxNbIter.value < props.limitsToFunctionKwargs.maxiter.min) {
        _maxNbIter.value = props.limitsToFunctionKwargs.maxiter.min;
        _recalculateWarning.value = true;
    }
    if (_maxNbIter.value > props.limitsToFunctionKwargs.maxiter.max) {
        _maxNbIter.value = props.limitsToFunctionKwargs.maxiter.max;
        _recalculateWarning.value = true;
    }

    if (_recalculateWarning.value) {
        // Return here if some parameters were modified
        event.preventDefault();
        return;
    }

    kwargs.value = {
        substrate: _periodicity.value,
        hardness: _enableHardness.value ? parseFloat(_hardness.value) : null,
        nsteps: _pressureSelection.value === "automatic" ? parseInt(_nbSteps.value) : null,
        pressures: _pressureSelection.value !== "automatic" ? _pressures.value : null,
        maxiter: parseInt(_maxNbIter.value),
    }

    emit('updateKwargs', kwargs.value);
}

function pressureValidator(str) {
    const value = parseFloat(str);
    if (!isNaN(value) && value > 0) {
        return true;
    }
    return false;
}

</script>

<template>
    <BModal v-model="visible"
            size="xl"
            title="Contact mechanics"
            ok-title="Run calculation"
            @ok="validateParameters">
        <!-- Substrate selection -->
        <BForm>
            <BInputGroup prepend="Type">
                <BFormSelect v-model="_periodicity">
                    <BFormSelectOption v-for="p in _periodicityOptions"
                                       :value="p.value">
                        {{ p.text }}
                    </BFormSelectOption>
                </BFormSelect>
            </BInputGroup>
            <div class="row mb-3">
                <div class="col-12">
                    <small>
                        This option determines how the elastic interactions are
                        calculated. This
                        affects edge effects
                        that may show up in the results at large contact area.
                        Calculations can
                        assume that the surface
                        repeats periodically or that it is pushing down on a
                        nonperiodic,
                        infinitely expanded
                        half-space.
                        The latter option corresponds to mapping the surface topography
                        on a
                        flat punch.
                    </small>
                </div>
            </div>

            <!-- _hardness input -->
            <BInputGroup prepend="Hardness" append-html="E<sup>*</sup>">
                <BInputGroupText>
                    <BFormCheckbox v-model="_enableHardness"></BFormCheckbox>
                </BInputGroupText>
                <BFormInput type="number"
                            min="0"
                            step="0.1"
                            v-model="_hardness"
                            :disabled="!_enableHardness">
                </BFormInput>
            </BInputGroup>
            <div class="row mb-3">
                <div class="col-12">
                    <small>
                        Setting a hardness enables plastic calculations. Local pressure
                        cannot
                        exceed the hardness
                        value.
                    </small>
                </div>
            </div>

            <!-- Step selection -->
            <!-- Automatic -->
            <BInputGroup>
                <BInputGroupText>
                    <BFormRadio value="automatic"
                                v-model="_pressureSelection">
                    </BFormRadio>
                </BInputGroupText>
                <BInputGroupText>
                    Number of steps
                </BInputGroupText>
                <BFormInput type="number"
                            :min="Math.max(2, limitsToFunctionKwargs.nsteps.min)"
                            :max="limitsToFunctionKwargs.nsteps.max"
                            step="1"
                            v-model="_nbSteps"
                            :disabled="_pressureSelection !== 'automatic'">
                </BFormInput>
            </BInputGroup>
            <div class="row mb-3">
                <div class="col-12">
                    <small>
                        Select this option to run a fully automatic calculation.
                        External
                        pressures are selected such
                        that contact area vs. pressure is approximately equally spaced
                        on a
                        log-log plot.
                    </small>
                </div>
            </div>
            <BInputGroup appendHtml="E<sup>*</sup>">
                <!-- Fixed list -->
                <BInputGroupText>
                    <BFormRadio value="manual"
                                v-model="_pressureSelection">
                    </BFormRadio>
                </BInputGroupText>
                <BInputGroupText>
                    Pressures
                </BInputGroupText>
                <BFormTags v-model="_pressures"
                           separator=" ,;"
                           placeholder="Enter pressure values separated by space, comma or semicolon"
                           remove-on-delete
                           :tag-validator="pressureValidator"
                           invalid-tag-text="Pressure value must be a positive number"
                           duplicate-tag-text="Duplicate pressure value"
                           :disabled="_pressureSelection === 'automatic'">
                </BFormTags>
            </BInputGroup>
            <div class="row mb-3">
                <div class="col-12">
                    <small>
                        Enter positive pressure values for which you need results. You
                        can also
                        copy/paste a
                        comma-separated list of values with a comma after every number.
                        Use dot
                        as decimal separator.
                        The maximum number of values is
                        {{ limitsToFunctionKwargs.pressures.maxlen }}.
                    </small>
                </div>
            </div>

            <!-- Input of maximum number of iterations -->
            <BInputGroup>
                <!-- Automatic -->
                <BInputGroupText>
                    Max. number of iterations
                </BInputGroupText>
                <BFormInput type="number"
                            :min="Math.max(1, limitsToFunctionKwargs.maxiter.min)"
                            :max="limitsToFunctionKwargs.maxiter.max"
                            step="100" class="form-control"
                            v-model="_maxNbIter">
                </BFormInput>
            </BInputGroup>
            <div class="row">
                <div class="col-12">
                    <small>
                        The calculation will stop if converged or after this maximum
                        number of
                        iterations. Data points
                        that are not converged are shown translucent in the resulting
                        plots. The
                        maximum number of
                        iterations is limited to {{
                            limitsToFunctionKwargs.maxiter.max
                        }}.
                    </small>
                </div>
            </div>

            <div class="alert alert-warning mt-2" v-if="_recalculateWarning">
                Some of the input parameters were invalid. We have updated those
                parameters for you.
                Please double-check
                the parameters and click <b>Run calculation</b> when ready.
            </div>
        </BForm>
    </BModal>
</template>