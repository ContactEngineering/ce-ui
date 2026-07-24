<script setup>

import {computed, ref} from "vue";

import {BButton, BDropdown, BDropdownItem, BSpinner} from 'bootstrap-vue-next';

import {countTaskStates} from '@/utils/tasks';

import BibliographyModal from '@/components/analysis/BibliographyModal.vue';
import CardExpandButton from '@/components/analysis/CardExpandButton.vue';
import TasksButton from '@/components/analysis/TasksButton.vue';
import HelpTooltip from '@/components/ui/HelpTooltip.vue';
import LoadingIndicator from '@/components/ui/LoadingIndicator.vue';
import Toolbar from '@/components/ui/Toolbar.vue';

const analyses = defineModel('analyses', {required: true});

const emit = defineEmits(['allTasksFinished', 'someTasksFinished', 'refreshButtonClicked']);

const props = defineProps({
    detailUrl: {
        type: String,
        default: '/ui/analysis-detail/'
    },
    description: {
        type: String,
        default: null
    },
    dois: {
        type: Array,
        default: null
    },
    referenceUrl: {
        type: String,
        default: null
    },
    enlarged: {
        type: Boolean,
        default: true
    },
    messages: {
        type: Array,
        default: []
    },
    functionName: {
      type: String,
      required: true
    },
    showLoadingSpinner: {
        type: Boolean,
        default: false
    },
    subjects: {
      type: Object,
      required: true
    },
    title: {
      type: String,
      required: true
    }
});

// GUI logic
const _bibliographyVisible = ref(false);

// Number of successful tasks
const nbSuccess = computed(() => {
    return countTaskStates(analyses.value, ['su']);
});

// Number of tasks that are not yet finished (pending, started or not-yet-run).
// While any of these remain we are still legitimately "waiting"; once none
// remain and there are still no successes, every task has failed.
const nbUnfinished = computed(() => {
    return countTaskStates(analyses.value, ['pe', 'st', 'no']);
});

</script>

<template>
    <div>
        <Toolbar justify="between">
            <div class="d-flex align-items-center gap-2">
                <BDropdown variant="primary" size="sm">
                    <template #button-content>
                        <i class="fa fa-bars"></i>
                    </template>
                    <BDropdownItem v-if="dois != null" @click="_bibliographyVisible = true">
                        Bibliography...
                    </BDropdownItem>
                    <slot name="dropdowns"></slot>
                </BDropdown>
                <span class="align-middle lead">
                    <b>{{ title }}</b>
                    <HelpTooltip v-if="description"
                                 class="ms-2 fs-6 align-middle"
                                 :text="description"
                                 :link-url="referenceUrl"
                                 link-text="Learn more in the paper"/>
                    <BSpinner class="ms-2" v-if="showLoadingSpinner" small/>
                </span>
            </div>
            <div class="btn-group btn-group-sm">
                <TasksButton v-if="analyses !== null"
                             v-model:analyses="analyses"
                             @allTasksFinished="(nbRunningOrPending) => emit('allTasksFinished', nbRunningOrPending)"
                             @someTasksFinished="(nbRunningOrPending) => emit('someTasksFinished', nbRunningOrPending)">
                </TasksButton>
                <BButton v-if="analyses !== null"
                         variant="primary"
                         size="sm"
                         @click="emit('refreshButtonClicked')">
                    <i class="fa fa-redo"></i>
                </BButton>
                <CardExpandButton v-if="!enlarged"
                                  :detail-url="detailUrl"
                                  :function-name="functionName"
                                  :subjects="subjects">
                </CardExpandButton>
            </div>
        </Toolbar>

        <LoadingIndicator v-if="analyses == null"/>

        <LoadingIndicator v-if="analyses != null && analyses.length > 0 && nbSuccess == 0 && nbUnfinished > 0"
                          message="Waiting for a first analysis task to complete..."/>

        <div v-if="analyses != null && analyses.length > 0 && nbSuccess == 0 && nbUnfinished == 0"
             class="tab-content">
            <div class="alert alert-danger">
                <i class="fa-solid fa-triangle-exclamation me-2"></i>All analysis
                tasks for this workflow failed, so there is nothing to display.
                Open the task status (the list icon above) for the error details,
                or use the refresh button to try again.
            </div>
        </div>

        <div v-if="analyses !== null && analyses.length > 0" class="tab-content">
            <div :class="['alert', message.alertClass]" v-for="message in messages">
                {{ message.message }}
            </div>
        </div>

        <div v-if="analyses != null && analyses.length === 0" class="tab-content">
            <div class="alert alert-secondary">
                <i class="fa-solid fa-circle-info me-2"></i>This analysis reported no results for the selected datasets.
            </div>
        </div>

        <div v-if="nbSuccess > 0" class="tab-content">
            <slot></slot>
        </div>
    </div>
    <BibliographyModal v-if="dois != null" v-model:visible="_bibliographyVisible" :dois="dois"></BibliographyModal>
</template>
