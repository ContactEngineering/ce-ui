<script lang="ts">
import axios from "axios";

/* Task states are polled in one batched request per card (see TasksButton);
   this row only displays them. It still fetches the workflow and subject
   descriptions for its header - through a cache shared by all rows (module
   scope, not per instance), since every row of a card asks for the same
   workflow, and rows for the same subject repeat too. */
const _sharedInfoCache = new Map();

function cachedGet(url) {
    if (!_sharedInfoCache.has(url)) {
        _sharedInfoCache.set(url, axios.get(url).then(response => response.data).catch(error => {
            // Do not cache failures
            _sharedInfoCache.delete(url);
            throw error;
        }));
    }
    return _sharedInfoCache.get(url);
}
</script>

<script setup lang="ts">

import {computed, ref, watch} from "vue";

import {BButton, useToast} from "bootstrap-vue-next";

import {formatDateTime, formatDuration, prettyBytes} from "@/utils/formatting";

import ProgressIndicator from "@/components/ui/ProgressIndicator.vue";

const toast = useToast();

const analysis = defineModel('analysis', {required: true});

const _error = ref(null);
const _function = ref(null);
const _subject = ref(null);

function fetchInfo() {
    if (_function.value == null && analysis.value.function != null) {
        cachedGet(analysis.value.function).then(data => {
            _function.value = data;
        }).catch(error => {
            toast.create({title: "Request failed", body: error, variant: 'danger'})?.show();
        });
    }

    if (_subject.value == null) {
        const subject = analysis.value.subject;
        const subjectUrl = subject.topography != null ?
            subject.topography : subject.surface != null ?
                subject.surface : subject.tag;
        if (subjectUrl == null) {
            toast.create({title: "Error", body: "Unable to determine subject for analysis", variant: 'danger'})?.show();
        } else {
            cachedGet(subjectUrl).then(data => {
                _subject.value = data;
            }).catch(error => {
                toast.create({title: "Request failed", body: error, variant: 'danger'})?.show();
            });
        }
    }
}

function fetchFailureReason() {
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
                    toast.create({title: "Request failed", body: error, variant: 'danger'})?.show();
                });
            }
        }).catch(error => {
            toast.create({title: "Request failed", body: error, variant: 'danger'})?.show();
        });
    }
}

function renew() {
    analysis.value.task_state = 'pe';  // The batched poller in TasksButton picks this up
    _error.value = null;
    // A PUT request triggers renewal of the analysis
    axios.put(analysis.value.url).then(response => {
        analysis.value = response.data;
    }).catch(error => {
        toast.create({title: "Request failed", body: error, variant: 'danger'})?.show();
    });
}

const taskMemoryPretty = computed(() => {
    return prettyBytes(analysis.value.task_memory);
});

const durationPretty = computed(() => formatDuration(analysis.value.task_duration));
const creationTimePretty = computed(() => formatDateTime(analysis.value.created_at || analysis.value.creation_time));
const startTimePretty = computed(() => formatDateTime(analysis.value.task_start_time));

watch(() => analysis.value, () => {
    fetchInfo();
    if (analysis.value.task_state === 'fa' && _error.value == null) {
        fetchFailureReason();
    }
}, {immediate: true});

</script>

<template>
    <tr>
        <td>
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
                    <template v-if="analysis.task_duration != null">&#8212; <b>Duration:</b> {{ durationPretty }}</template></span>
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
            <!-- Wide progress bar underneath the task description. -->
            <ProgressIndicator
                class="mt-2"
                :value="analysis.task_progress == null ? 0 : analysis.task_progress"
                :state="analysis.task_state">
            </ProgressIndicator>
        </td>
        <td class="align-middle text-end" style="width:120px">
            <BButton variant="outline-primary"
                     size="sm"
                     :disabled="analysis.task_state === 'pe' || analysis.task_state === 'st'"
                     :title="analysis.task_state === 'pe' || analysis.task_state === 'st'
                             ? 'This task is already queued or running'
                             : 'Discard the result and run this analysis again'"
                     @click="renew">
                <i class="fa fa-rotate-right me-1"></i>Renew
            </BButton>
        </td>
    </tr>
</template>
