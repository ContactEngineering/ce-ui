<script setup>

import { computed, ref } from "vue";

import {
    QCard,
    QCardSection,
    QBtn,
    QBtnDropdown,
    QList,
    QItem,
    QItemSection,
    QSeparator,
    QSpinner,
    QBanner
} from 'quasar';

import { countTaskStates } from 'topobank/utils/tasks.ts';

import BibliographyModal from './BibliographyModal.vue';
import CardExpandButton from './CardExpandButton.vue';
import TasksButton from './TasksButton.vue';

const analyses = defineModel('analyses', { required: true });

const emit = defineEmits(['allTasksFinished', 'someTasksFinished', 'refreshButtonClicked']);

const props = defineProps({
    detailUrl: {
        type: String,
        default: '/ui/analysis-detail/'
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

</script>

<template>
    <QCard>
        <QCardSection class="bg-grey-2 flex items-center">
            <QBtnDropdown flat size="sm" class="q-mr-sm">
                <template #label>
                    <i class="fa fa-bars"></i>
                </template>
                <QList>
                    <QItem v-if="dois != null" clickable v-close-popup @click="_bibliographyVisible = true">
                        <QItemSection>Bibliography...</QItemSection>
                    </QItem>
                    <slot name="dropdowns"></slot>
                </QList>
            </QBtnDropdown>
            <span class="text-subtitle1 text-weight-bold">
                {{ title }}
                <QSpinner class="q-ml-sm" v-if="showLoadingSpinner" size="sm" />
            </span>
            <div class="q-ml-auto flex items-center q-gutter-xs">
                <TasksButton v-if="analyses !== null"
                             v-model:analyses="analyses"
                             @allTasksFinished="(nbRunningOrPending) => emit('allTasksFinished', nbRunningOrPending)"
                             @someTasksFinished="(nbRunningOrPending) => emit('someTasksFinished', nbRunningOrPending)">
                </TasksButton>
                <QBtn v-if="analyses !== null"
                      flat
                      size="sm"
                      @click="emit('refreshButtonClicked')">
                    <i class="fa fa-redo"></i>
                </QBtn>
                <CardExpandButton v-if="!enlarged"
                                  :detail-url="detailUrl"
                                  :function-name="functionName"
                                  :subjects="subjects">
                </CardExpandButton>
            </div>
        </QCardSection>

        <QCardSection>
            <div v-if="analyses == null" class="flex justify-center q-mt-lg">
                <div class="column items-center">
                    <QSpinner size="lg" />
                    <p class="q-mt-sm">Loading...</p>
                </div>
            </div>

            <div v-if="analyses != null && analyses.length > 0 && nbSuccess == 0"
                 class="flex justify-center q-mt-lg">
                <div class="column items-center">
                    <QSpinner size="lg" />
                    <p class="q-mt-sm">Waiting for a first analysis task to complete...</p>
                </div>
            </div>

            <div v-if="analyses !== null && analyses.length > 0">
                <QBanner v-for="(message, index) in messages" :key="index"
                         :class="message.alertClass"
                         class="q-mb-sm">
                    {{ message.message }}
                </QBanner>
            </div>

            <div v-if="analyses != null && analyses.length === 0">
                <h5>This analysis reported no results for the selected datasets.</h5>
            </div>

            <div v-if="nbSuccess > 0">
                <slot></slot>
            </div>
        </QCardSection>
    </QCard>
    <BibliographyModal v-if="dois != null" v-model:visible="_bibliographyVisible" :dois="dois"></BibliographyModal>
</template>
