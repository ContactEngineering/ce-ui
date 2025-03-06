<script setup>

import {computed, ref} from "vue";

import {BButton, BCard, BDropdown, BDropdownItem, BSpinner} from 'bootstrap-vue-next';

import {countTaskStates} from 'topobank/utils/tasks.js';

import BibliographyModal from './BibliographyModal.vue';
import CardExpandButton from './CardExpandButton.vue';
import TasksButton from './TasksButton.vue';

const analyses = defineModel('analyses', {required: true});

const emit = defineEmits(['allTasksFinished', 'someTasksFinished', 'refreshButtonClicked']);

const props = defineProps({
    detailUrl: {
        type: String,
        default: '/ui/html/analysis-detail/'
    },
    dois: {
        type: Array,
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
    functionId: {
      type: Number,
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

</script>

<template>
    <BCard :header="title">
        <template #header>
            <div class="btn-group btn-group-sm float-end">
                <TasksButton v-if="analyses !== null"
                             v-model:analyses="analyses"
                             @allTasksFinished="(nbRunningOrPending) => emit('allTasksFinished', nbRunningOrPending)"
                             @someTasksFinished="(nbRunningOrPending) => emit('someTasksFinished', nbRunningOrPending)">
                </TasksButton>
                <BButton v-if="analyses !== null"
                         variant="outline-secondary"
                         size="sm"
                         @click="emit('refreshButtonClicked')"
                         class="float-end ms-1">
                    <i class="fa fa-redo"></i>
                </BButton>
                <CardExpandButton v-if="!enlarged"
                                  :detail-url="detailUrl"
                                  :function-id="functionId"
                                  :subjects="subjects"
                                  class="float-end">
                </CardExpandButton>
            </div>
            <BDropdown variant="outline-secondary" size="sm" class="float-start me-2">
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
                <BSpinner class="ms-2" v-if="showLoadingSpinner" small/>
            </span>
        </template>
        <div v-if="analyses == null" class="d-flex justify-content-center mt-5">
            <div class="flex-column text-center">
                <b-spinner/>
                <p>Loading...</p>
            </div>
        </div>

        <div v-if="analyses != null && analyses.length > 0 && nbSuccess == 0"
             class="d-flex justify-content-center mt-5">
            <div class="flex-column text-center">
                <b-spinner/>
                <p>Waiting for a first analysis task to complete...</p>
            </div>
        </div>

        <div v-if="analyses !== null && analyses.length > 0" class="tab-content">
            <div :class="['alert', message.alertClass]" v-for="message in messages">
                {{ message.message }}
            </div>
        </div>

        <div v-if="analyses != null && analyses.length === 0" class="tab-content">
            <h5>This analysis reported no results for the selected datasets.</h5>
        </div>

        <div v-if="nbSuccess > 0" class="tab-content">
            <slot></slot>
        </div>
    </BCard>
    <BibliographyModal v-if="dois != null" v-model:visible="_bibliographyVisible" :dois="dois"></BibliographyModal>
</template>
