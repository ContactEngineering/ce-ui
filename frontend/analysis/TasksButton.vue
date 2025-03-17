<script setup>

import {computed, ref} from "vue";

import {BButton} from 'bootstrap-vue-next';

import {countTaskStates} from 'topobank/utils/tasks.ts';

import TaskStatesModal from './TaskStatesModal.vue';

// List of analyses
const analyses = defineModel('analyses', {required: true});

// Event when all tasks are finished
const emit = defineEmits(['allTasksFinished', 'someTasksFinished']);

// UI logic
const _modalVisible = ref(false);

// Number of running or pending tasks
let _lastNbRunningOrPending = null;
const nbRunningOrPending = computed(() => {
    const currentNbRunningOrPending = countTaskStates(analyses.value, ['pe', 'st', 're']);
    // Emit event when all tasks are finished
    if (_lastNbRunningOrPending !== null && _lastNbRunningOrPending > 0) {
        if (currentNbRunningOrPending === 0) {
            emit('allTasksFinished', currentNbRunningOrPending);
        } else if (currentNbRunningOrPending < _lastNbRunningOrPending) {
            emit('someTasksFinished', currentNbRunningOrPending);
        }
    }
    _lastNbRunningOrPending = currentNbRunningOrPending;
    return currentNbRunningOrPending;
});

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
    <BButton variant="light"
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
