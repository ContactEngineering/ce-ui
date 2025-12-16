<script setup>

import { computed, ref } from "vue";

import { QBtn, QBadge, QSpinner } from 'quasar';

import { countTaskStates } from 'topobank/utils/tasks.ts';

import TaskStatesModal from './TaskStatesModal.vue';

// List of analyses
const analyses = defineModel('analyses', { required: true });

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
    <QBtn flat size="sm" @click="_modalVisible = !_modalVisible">
        <QSpinner v-if="nbRunningOrPending > 0" size="xs" class="q-mr-xs" />
        Tasks
        <QBadge v-if="nbRunningOrPending > 0" color="grey" class="q-ml-xs">{{ nbRunningOrPending }}</QBadge>
        <QBadge v-if="nbSuccess > 0" color="positive" class="q-ml-xs">{{ nbSuccess }}</QBadge>
        <QBadge v-if="nbFailed > 0" color="negative" class="q-ml-xs">{{ nbFailed }}</QBadge>
    </QBtn>
    <TaskStatesModal v-model:visible="_modalVisible"
                     v-model:analyses="analyses">
    </TaskStatesModal>
</template>
