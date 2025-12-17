<script setup>

import { ref } from "vue";

import {
    QDialog,
    QCard,
    QCardSection,
    QCardActions,
    QBtn,
    QSelect,
    QInput,
    QCheckbox,
    QRadio,
    QBanner
} from "quasar";

const visible = defineModel('visible', { required: true });
const kwargs = defineModel('kwargs', { required: true });

const emit = defineEmits(['updateKwargs']);

const props = defineProps({
    limitsToFunctionKwargs: Object,
});

const _enableHardness = ref(kwargs.value === undefined ? false : kwargs.value.hardness !== null);
const _hardness = ref(kwargs.value === undefined ? null : kwargs.value.hardness);
const _maxNbIter = ref(kwargs.value === undefined ? 100 : kwargs.value.maxiter);
const _nbSteps = ref(kwargs.value === undefined ? 10 : kwargs.value.nsteps);
const _periodicity = ref(kwargs.value === undefined ? "nonperiodic" : kwargs.value.substrate);
const _periodicityOptions = [
    { value: "periodic", label: "Periodic (repeating array of the measurement)" },
    { value: "nonperiodic", label: "Free boundaries (flat punch with measurement)" }
];
const _pressureSelection = ref(kwargs.value == null ? "automatic" :
    (kwargs.value.pressures == null ? "automatic" : "manual"));
const _pressuresInput = ref(kwargs.value == null ? "" :
    (kwargs.value.pressures == null ? "" : kwargs.value.pressures.join(", ")));
const _recalculateWarning = ref(false);

function validateParameters() {
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
        if (_nbSteps.value > props.limitsToFunctionKwargs.nsteps.max) {
            _nbSteps.value = props.limitsToFunctionKwargs.nsteps.max;
            _recalculateWarning.value = true;
        }
    } else { // pressure_selection_mode == "manual"
        // Parse pressures from input string
        const pressureStrings = _pressuresInput.value.split(/[ ,;]+/).filter(s => s.length > 0);
        pressures = pressureStrings.map(parseFloat).filter(p => {
            return !isNaN(p) && p > 0
        }).sort((a, b) => a - b);

        if (pressures.length < 1) {
            pressures = [1];
            _recalculateWarning.value = true;
        } else if (pressures.length > props.limitsToFunctionKwargs.pressures.maxlen) {
            pressures.length = props.limitsToFunctionKwargs.pressures.maxlen;
            _recalculateWarning.value = true;
        }
        _pressuresInput.value = pressures.join(", ");
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
        return;
    }

    kwargs.value = {
        substrate: _periodicity.value,
        hardness: _enableHardness.value ? parseFloat(_hardness.value) : null,
        nsteps: _pressureSelection.value === "automatic" ? parseInt(_nbSteps.value) : null,
        pressures: _pressureSelection.value !== "automatic" ? pressures : null,
        maxiter: parseInt(_maxNbIter.value),
    }

    visible.value = false;
    emit('updateKwargs', kwargs.value);
}

</script>

<template>
    <QDialog v-model="visible">
        <QCard style="min-width: 600px; max-width: 900px">
            <QCardSection>
                <div class="text-h6">Contact mechanics</div>
            </QCardSection>
            <QCardSection>
                <!-- Substrate selection -->
                <QSelect
                    v-model="_periodicity"
                    :options="_periodicityOptions"
                    label="Type"
                    emit-value
                    map-options
                    outlined
                    class="q-mb-sm"
                />
                <p class="text-caption text-grey q-mb-md">
                    This option determines how the elastic interactions are calculated. This affects edge effects
                    that may show up in the results at large contact area. Calculations can assume that the surface
                    repeats periodically or that it is pushing down on a nonperiodic, infinitely expanded half-space.
                    The latter option corresponds to mapping the surface topography on a flat punch.
                </p>

                <!-- Hardness input -->
                <div class="row items-center q-mb-sm">
                    <div class="col-auto">
                        <QCheckbox v-model="_enableHardness" label="Enable hardness" />
                    </div>
                    <div class="col">
                        <QInput
                            v-model.number="_hardness"
                            type="number"
                            label="Hardness (E*)"
                            :min="0"
                            step="0.1"
                            :disable="!_enableHardness"
                            outlined
                            dense
                        />
                    </div>
                </div>
                <p class="text-caption text-grey q-mb-md">
                    Setting a hardness enables plastic calculations. Local pressure cannot exceed the hardness value.
                </p>

                <!-- Step selection - Automatic -->
                <div class="row items-center q-mb-sm">
                    <div class="col-auto">
                        <QRadio v-model="_pressureSelection" val="automatic" label="Number of steps" />
                    </div>
                    <div class="col">
                        <QInput
                            v-model.number="_nbSteps"
                            type="number"
                            :min="Math.max(2, limitsToFunctionKwargs.nsteps.min)"
                            :max="limitsToFunctionKwargs.nsteps.max"
                            step="1"
                            :disable="_pressureSelection !== 'automatic'"
                            outlined
                            dense
                        />
                    </div>
                </div>
                <p class="text-caption text-grey q-mb-md">
                    Select this option to run a fully automatic calculation. External pressures are selected such
                    that contact area vs. pressure is approximately equally spaced on a log-log plot.
                </p>

                <!-- Step selection - Manual pressures -->
                <div class="row items-center q-mb-sm">
                    <div class="col-auto">
                        <QRadio v-model="_pressureSelection" val="manual" label="Pressures (E*)" />
                    </div>
                    <div class="col">
                        <QInput
                            v-model="_pressuresInput"
                            label="Enter pressure values separated by space, comma or semicolon"
                            :disable="_pressureSelection === 'automatic'"
                            outlined
                            dense
                        />
                    </div>
                </div>
                <p class="text-caption text-grey q-mb-md">
                    Enter positive pressure values for which you need results. You can also copy/paste a
                    comma-separated list of values with a comma after every number. Use dot as decimal separator.
                    The maximum number of values is {{ limitsToFunctionKwargs.pressures.maxlen }}.
                </p>

                <!-- Maximum iterations -->
                <QInput
                    v-model.number="_maxNbIter"
                    type="number"
                    label="Max. number of iterations"
                    :min="Math.max(1, limitsToFunctionKwargs.maxiter.min)"
                    :max="limitsToFunctionKwargs.maxiter.max"
                    step="100"
                    outlined
                    class="q-mb-sm"
                />
                <p class="text-caption text-grey q-mb-md">
                    The calculation will stop if converged or after this maximum number of iterations. Data points
                    that are not converged are shown translucent in the resulting plots. The maximum number of
                    iterations is limited to {{ limitsToFunctionKwargs.maxiter.max }}.
                </p>

                <QBanner v-if="_recalculateWarning" class="bg-warning text-white q-mt-md">
                    Some of the input parameters were invalid. We have updated those parameters for you.
                    Please double-check the parameters and click <b>Run calculation</b> when ready.
                </QBanner>
            </QCardSection>
            <QCardActions align="right">
                <QBtn flat label="Cancel" v-close-popup />
                <QBtn color="primary" label="Run calculation" @click="validateParameters" />
            </QCardActions>
        </QCard>
    </QDialog>
</template>