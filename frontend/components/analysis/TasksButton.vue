<script setup>

import {computed, ref, watch} from "vue";

import {BButton} from 'bootstrap-vue-next';

import {countTaskStates} from '@/utils/tasks';

import TaskStatesModal from '@/components/analysis/TaskStatesModal.vue';

// List of analyses
const analyses = defineModel('analyses', {required: true});

// Event when all tasks are finished
const emit = defineEmits(['allTasksFinished', 'someTasksFinished']);

// UI logic
const _modalVisible = ref(false);

// Number of running or pending tasks
const nbRunningOrPending = computed(() => {
    return countTaskStates(analyses.value, ['pe', 'st', 're']);
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
