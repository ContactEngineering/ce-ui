<script setup>

import {computed, ref} from "vue";

import {BModal, BPagination} from "bootstrap-vue-next";

import TaskStateRow from "@/components/analysis/TaskStateRow.vue";

// Visibility of the modal
const visible = defineModel('visible', {required: true});

// List of analyses
const analyses = defineModel('analyses', {required: true});

const _currentPage = ref(1);
const _perPage = ref(10);

// The slice of analyses shown on the current page, each paired with its index
// in the original list so the row can two-way bind to (and update) the right
// entry as it polls.
const _pageItems = computed(() => {
    const start = (_currentPage.value - 1) * _perPage.value;
    return analyses.value
        .slice(start, start + _perPage.value)
        .map((analysis, i) => ({analysis, index: start + i}));
});

</script>

<template>
    <BModal v-model="visible"
            size="xl"
            title="Tasks"
            :ok-only="true"
            ok-title="Close">
        <small v-if="analyses.length > 0">
            <table class="table table-hover task-table">
                <tbody>
                <TaskStateRow v-for="item in _pageItems"
                              :key="item.index"
                              v-model:analysis="analyses[item.index]">
                </TaskStateRow>
                </tbody>
            </table>
        </small>
        <BPagination v-if="analyses.length > _perPage"
                     v-model="_currentPage"
                     :total-rows="analyses.length"
                     :per-page="_perPage"
                     align="center"
                     size="sm"
                     class="mb-0">
        </BPagination>
        <div v-if="analyses.length === 0" class="alert alert-secondary">
            <i class="fa-solid fa-circle-info me-2"></i>No analysis was triggered for this function and these subjects.
        </div>
    </BModal>
</template>
