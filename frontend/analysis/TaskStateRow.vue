<script setup lang="ts">

import {computed, onMounted, onBeforeUnmount, ref, watch} from "vue";

import {BButton, useToastController} from "bootstrap-vue-next";

import {
    analysisApiWorkflowRetrieve,
    analysisApiResultRetrieve,
    analysisApiResultUpdate,
    managerApiSurfaceRetrieve,
    managerApiTopographyRetrieve,
    filesFolderRetrieve
} from "@/api";
import {getIdFromUrl} from "@/utils/api";

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

async function scheduleStateCheck() {
    // Tasks are still pending or running if this state check is scheduled

    // Get function information if we don't have it yet
    if (_function.value == null) {
        try {
            const workflowId = getIdFromUrl(analysis.value.function);
            const response = await analysisApiWorkflowRetrieve({path: {id: workflowId}});
            _function.value = response.data;
        } catch (error: any) {
            show?.({props: {title: "Request failed", body: error.message, variant: 'danger'}});
        }
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
            try {
                const subjectId = getIdFromUrl(subjectUrl);
                if (subject.topography != null) {
                    const response = await managerApiTopographyRetrieve({path: {id: subjectId}});
                    _subject.value = response.data;
                } else if (subject.surface != null) {
                    const response = await managerApiSurfaceRetrieve({path: {id: subjectId}});
                    _subject.value = response.data;
                } else {
                    // Tag - keep as fallback, may need specific API
                    show?.({props: {title: "Warning", body: "Tag subjects not fully supported", variant: 'warning'}});
                }
            } catch (error: any) {
                show?.({props: {title: "Request failed", body: error.message, variant: 'danger'}});
            }
        }
    }

    if (analysis.value.task_state == null || analysis.value.task_state === 'pe' || analysis.value.task_state === 'st') {
        if (_timeoutID == null) {
            _timeoutID = setTimeout(checkState, props.pollingInterval);
        }
    } else if (analysis.value.task_state === 'fa') {
        // This is a failure. Query reason.
        if (analysis.value.error == null) {
            // The analysis function did not raise an exception itself. This means it actually finished and
            // we have a result.json, that should contain an error message.
            try {
                const folderId = getIdFromUrl(analysis.value.folder);
                const folderResponse = await filesFolderRetrieve({path: {id: folderId}});
                // The folder response contains file URLs - we need to fetch result.json
                // Note: The file URL is external (S3/storage), keeping as fetch
                const resultFile = folderResponse.data["result.json"];
                if (resultFile?.url) {
                    const response = await fetch(resultFile.url);
                    const data = await response.json();
                    _error.value = data.message;
                }
            } catch (error: any) {
                console.error("Failed to fetch error details:", error);
            }
        } else {
            // The analysis function failed and we have an error message (Python exception).
            _error.value = analysis.value.error;
        }
    }
}

async function checkState() {
    _timeoutID = null;  // Indicate that no timer is currently running
    try {
        const resultId = getIdFromUrl(analysis.value.url);
        const response = await analysisApiResultRetrieve({path: {id: resultId}});
        // Update current state of the analysis
        analysis.value = response.data;  // This will trigger a check through a watch
    } catch (error: any) {
        show?.({props: {title: "Request failed", body: error.message, variant: 'danger'}});
    }
}

async function renew() {
    analysis.value.task_state = 'pe';
    // A PUT request triggers renewal of the analysis
    try {
        const resultId = getIdFromUrl(analysis.value.url);
        const response = await analysisApiResultUpdate({path: {id: resultId}});
        analysis.value = response.data;  // This will trigger a check through a watch
    } catch (error: any) {
        show?.({props: {title: "Request failed", body: error.message, variant: 'danger'}});
    }
}

const taskMemoryPretty = computed(() => {
    return prettyBytes(analysis.value.task_memory);
});

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
                <span><b>Created on:</b> {{ new Date(analysis.creation_time).toLocaleString() }}
                    &#8212; <b>Started at:</b> {{ new Date(analysis.start_time).toLocaleString() }}
                    &#8212; <b>Duration:</b> {{ analysis.duration }}</span>
                <span v-if="analysis.task_memory != null">
                    &#8212; <b>Peak memory usage:</b> {{ taskMemoryPretty }}
                </span>
            </div>
            <div v-if="analysis.task_state === 'fa'">
                This task was created on {{ new Date(analysis.creation_time).toLocaleString() }},
                started running {{ new Date(analysis.start_time).toLocaleString() }}
                but failed
                <span v-if="_error != null">
                    with message: <i>{{ _error }}</i>
                </span>
                <span v-if="_error == null">.</span>
            </div>
            <div v-if="analysis.task_state === 'pe'">
                This task was created on {{ new Date(analysis.creation_time).toLocaleString() }} and is
                currently waiting to be started.
            </div>
            <div v-if="analysis.task_state === 'st'">
                This task was created on {{ new Date(analysis.creation_time).toLocaleString() }}, started
                {{ new Date(analysis.start_time).toLocaleString() }}
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
