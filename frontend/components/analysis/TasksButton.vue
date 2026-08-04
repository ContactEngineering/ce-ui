<script setup>

import axios from "axios";
import {computed, onBeforeUnmount, ref, watch} from "vue";

import {BButton} from 'bootstrap-vue-next';

import {countTaskStates} from '@/utils/tasks';

import TaskStatesModal from '@/components/analysis/TaskStatesModal.vue';

// List of analyses
const analyses = defineModel('analyses', {required: true});

// Event when all tasks are finished
const emit = defineEmits(['allTasksFinished', 'someTasksFinished']);

const props = defineProps({
    pollingInterval: {
        type: Number,
        default: 5000  // milliseconds
    },
    maxPollingInterval: {
        type: Number,
        default: 30000  // milliseconds
    }
});

// UI logic
const _modalVisible = ref(false);

// Number of running or pending tasks
const nbRunningOrPending = computed(() => {
    return countTaskStates(analyses.value, ['pe', 'st', 're']);
});

/* Batched task polling: while any task of this card is pending or running, the
   task states of all of them are fetched in a single request per tick, rather
   than every task polling its own detail route (which meant one request per
   analysis every few seconds during a bulk run). Poll quickly at first, then
   back off; the backoff resets whenever a drained card picks up new pending
   tasks (e.g. the user renews one). */

// Task fields the poll merges into the analyses. Everything else keeps the
// shape the card endpoint delivered, so displays bound to it are unaffected.
const TASK_FIELDS = [
    'task_state',
    'task_progress',
    'task_messages',
    'task_error',
    'task_traceback',
    'task_memory',
    'task_duration',
    'task_submission_time',
    'task_start_time',
    'task_end_time'
];

// The endpoint caps `limit` at this value; poll in chunks
const MAX_BATCH_SIZE = 100;

let _timeoutID = null;
let _currentPollingInterval = props.pollingInterval;

function pendingIds() {
    if (analyses.value == null) {
        return [];
    }
    return analyses.value
        .filter(a => a != null && ['pe', 'st', 're'].includes(a.task_state))
        .map(a => a.id);
}

async function poll() {
    _timeoutID = null;
    const ids = pendingIds();
    if (ids.length === 0) {
        return;
    }
    try {
        const updated = new Map();
        for (let start = 0; start < ids.length; start += MAX_BATCH_SIZE) {
            const chunk = ids.slice(start, start + MAX_BATCH_SIZE);
            const response = await axios.get(
                `/analysis/v2/results/?ids=${chunk.join(',')}&limit=${chunk.length}`);
            for (const result of response.data.results ?? response.data) {
                updated.set(result.id, result);
            }
        }
        analyses.value = analyses.value.map(analysis => {
            const update = updated.get(analysis?.id);
            if (update == null) {
                return analysis;
            }
            const merged = {...analysis};
            for (const field of TASK_FIELDS) {
                if (field in update) {
                    merged[field] = update[field];
                }
            }
            return merged;
        });
    } catch (error) {
        // Transient failure; the next tick retries
    }
    scheduleNextPoll();
}

function scheduleNextPoll() {
    if (pendingIds().length === 0 || _timeoutID != null) {
        return;
    }
    _timeoutID = setTimeout(poll, _currentPollingInterval);
    _currentPollingInterval = Math.min(
        _currentPollingInterval * 1.5, props.maxPollingInterval);
}

onBeforeUnmount(() => {
    if (_timeoutID != null) {
        clearTimeout(_timeoutID);
        _timeoutID = null;
    }
});

// Tell the parent when tasks finish. A watcher only fires when the count
// actually changes, so parents can safely react by re-fetching data.
watch(nbRunningOrPending, (current, previous) => {
    if (previous > 0) {
        if (current === 0) {
            emit('allTasksFinished', current);
        } else if (current < previous) {
            emit('someTasksFinished', current);
        }
    }
    if (current > 0) {
        if (previous == null || previous === 0) {
            // A fresh batch of tasks: start polling promptly again
            _currentPollingInterval = props.pollingInterval;
        }
        scheduleNextPoll();
    }
}, {immediate: true});

// Number of successful tasks
const nbSuccess = computed(() => {
    return countTaskStates(analyses.value, ['su']);
});

// Number of failed tasks
const nbFailed = computed(() => {
    return countTaskStates(analyses.value, ['fa']);
});

</script>

<template>
    <BButton variant="primary"
             size="sm"
             @click="_modalVisible = !_modalVisible">
        <span v-if="nbRunningOrPending > 0" class="spinner"></span>
        Tasks
        <span v-if="nbRunningOrPending > 0" class="badge bg-secondary ms-1">{{ nbRunningOrPending }}</span>
        <span v-if="nbSuccess > 0" class="badge bg-success ms-1">{{ nbSuccess }}</span>
        <span v-if="nbFailed > 0" class="badge bg-danger ms-1">{{ nbFailed }}</span>
    </BButton>
    <TaskStatesModal v-model:visible="_modalVisible"
                     v-model:analyses="analyses">
    </TaskStatesModal>
</template>
