<script setup>

import {
    QDialog,
    QCard,
    QCardSection,
    QCardActions,
    QBtn,
    QMarkupTable,
    QBanner
} from "quasar";

import TaskStateRow from "./TaskStateRow.vue";

// Visibility of the modal
const visible = defineModel('visible', { required: true });

// List of analyses
const analyses = defineModel('analyses', { required: true });

</script>

<template>
    <QDialog v-model="visible" maximized>
        <QCard>
            <QCardSection>
                <div class="text-h6">Tasks</div>
            </QCardSection>
            <QCardSection>
                <QMarkupTable v-if="analyses.length > 0" class="text-caption">
                    <thead>
                    <tr>
                        <th class="text-left" style="width:100px"></th>
                        <th class="text-left">Task description</th>
                        <th class="text-left" style="width:150px">Actions</th>
                    </tr>
                    </thead>
                    <tbody>
                    <TaskStateRow v-for="(analysis, i) in analyses"
                                  :key="analysis.id || i"
                                  v-model:analysis="analyses[i]">
                    </TaskStateRow>
                    </tbody>
                </QMarkupTable>
                <QBanner v-if="analyses.length === 0" class="bg-info text-white">
                    No analysis was triggered for this function and these subjects.
                </QBanner>
            </QCardSection>
            <QCardActions align="right">
                <QBtn flat label="Close" v-close-popup />
            </QCardActions>
        </QCard>
    </QDialog>
</template>
