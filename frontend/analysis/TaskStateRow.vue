<script setup lang="ts">

import axios from "axios";
import {computed, onMounted, onBeforeUnmount, ref, watch} from "vue";

import {BButton, useToastController} from "bootstrap-vue-next";

import {prettyBytes} from "../utils/formatting";

import ProgressIndicator from "topobank/components/ProgressIndicator.vue";

const {show} = useToastController();

const analysis = defineModel('analysis', {required: true});

const props = defineProps({
    pollingInterval: {
        type: Number,
        default: 2000  // milliseconds
    }
});

const _error = ref(null);
const _function = ref(null);
const _subject = ref(null);
let _timeoutID = null;

onMounted(() => {
    scheduleStateCheck();
});

onBeforeUnmount(() => {
    if (_timeoutID != null) {
        clearTimeout(_timeoutID);
        _timeoutID = null;
    }
});

function scheduleStateCheck() {
    // Tasks are still pending or running if this state check is scheduled

    // Get function information if we don't have it yet
    if (_function.value == null) {
        axios.get(analysis.value.function)
            .then(response => {
                _function.value = response.data;
            }).catch(error => {
            show?.({props: {title: "Request failed", body: error, variant: 'danger'}});
        });
    }

    // Get subject information if we don't have it yet
    if (_subject.value == null) {
        const subject = analysis.value.subject;
        const subjectUrl = subject.topography != null ?
            subject.topography : subject.surface != null ?
                subject.surface : subject.tag;
        if (subjectUrl == null) {
            show?.({props: {title: "Error", body: "Unable to determine subject for analysis", variant: 'danger'}});
        } else {
            axios.get(subjectUrl)
                .then(response => {
                    _subject.value = response.data;
                }).catch(error => {
                show?.({props: {title: "Request failed", body: error, variant: 'danger'}});
            });
        }
    }

    if (analysis.value.task_state == null || analysis.value.task_state === 'pe' || analysis.value.task_state === 'st') {
        if (_timeoutID == null) {
            _timeoutID = setTimeout(checkState, props.pollingInterval);
        }
    } else if (analysis.value.task_state === 'fa') {
        // This is a failure. Query reason.
        if (analysis.value.task_error) {
            // The analysis function failed and we have an error message (Python exception).
            _error.value = analysis.value.task_error;
        } else {
            // The analysis function did not raise an exception itself. This means it actually finished and
            // we have a result.json, that should contain an error message.
            axios.get(analysis.value.folder).then(response => {
                const resultFile = response.data["result.json"];
                if (resultFile?.url != null) {
                    axios.get(resultFile.url).then(response => {
                        _error.value = response.data.message;
                    }).catch(error => {
                        show?.({props: {title: "Request failed", body: error, variant: 'danger'}});
                    });
                }
            }).catch(error => {
                show?.({props: {title: "Request failed", body: error, variant: 'danger'}});
            });
        }
    }
}

function checkState() {
    _timeoutID = null;  // Indicate that no timer is currently running
    axios.get(analysis.value.url).then(response => {
        // Update current state of the analysis
        analysis.value = response.data;  // This will trigger a check throw a watch
    }).catch(error => {
        show?.({props: {title: "Request failed", body: error, variant: 'danger'}});
    });
}

function renew() {
    analysis.value.task_state = 'pe';
    // A PUT request triggers renewal of the analysis
    axios.put(analysis.value.url).then(response => {
        analysis.value = response.data;  // This will trigger a check throw a watch
    }).catch(error => {
        show?.({props: {title: "Request failed", body: error, variant: 'danger'}});
    });
}

const taskMemoryPretty = computed(() => {
    return prettyBytes(analysis.value.task_memory);
});

// Format an ISO date string for display, returning null for missing/invalid
// values (e.g. a failed task that never started has no start time).
function formatDateTime(value) {
    if (value == null) {
        return null;
    }
    const date = new Date(value);
    return isNaN(date.getTime()) ? null : date.toLocaleString();
}

const creationTimePretty = computed(() => formatDateTime(analysis.value.creation_time));
const startTimePretty = computed(() => formatDateTime(analysis.value.task_start_time));

watch(() => analysis.value, () => {
    scheduleStateCheck();
});

</script>

<template>
    <tr>
        <td>
            <ProgressIndicator
                :value="analysis.task_progress == null ? 0 : analysis.task_progress"
                :state="analysis.task_state">
            </ProgressIndicator>
        </td>
        <td v-if="analysis == null">
            <p>Fetching analysis status, please wait...</p>
        </td>
        <td v-if="analysis != null">
            <div v-if="_function == null || _subject == null">
                <div class="spinner"></div>
                Retrieving function information...
            </div>
            <div v-if="_function != null && _subject != null">
                <b>Function <i>{{ _function.display_name }}</i> on subject <i>{{
                        _subject.name
                    }}</i></b>
            </div>
            <div>
                <b>Parameters:</b> {{ analysis.kwargs }}
            </div>
            <div v-if="analysis.task_state === 'su'">
                <span><b>Created on:</b> {{ creationTimePretty }}
                    <template v-if="startTimePretty != null">&#8212; <b>Started at:</b> {{ startTimePretty }}</template>
                    <template v-if="analysis.task_duration != null">&#8212; <b>Duration:</b> {{ analysis.task_duration }}</template></span>
                <span v-if="analysis.task_memory != null">
                    &#8212; <b>Peak memory usage:</b> {{ taskMemoryPretty }}
                </span>
            </div>
            <div v-if="analysis.task_state === 'fa'">
                This task was created on {{ creationTimePretty }}<template v-if="startTimePretty != null">, started running {{ startTimePretty }}</template>
                but failed<span v-if="_error != null"> with message: <i>{{ _error }}</i></span><span v-else>.</span>
            </div>
            <div v-if="analysis.task_state === 'pe'">
                This task was created on {{ creationTimePretty }} and is
                currently waiting to be started.
            </div>
            <div v-if="analysis.task_state === 'st'">
                This task was created on {{ creationTimePretty }}<template v-if="startTimePretty != null">, started
                {{ startTimePretty }}</template>
                and is currently running.
            </div>
        </td>
        <td>
            <BButton @click="renew">
                Renew
            </BButton>
        </td>
    </tr>
</template>
