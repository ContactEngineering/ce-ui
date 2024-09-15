<script setup>

import {BModal} from "bootstrap-vue-next";

import TaskStateRow from "./TaskStateRow.vue";

// Visibility of the modal
const visible = defineModel('visible', {required: true});

// List of analyses
const analyses = defineModel('analyses', {required: true});

</script>

<template>
    <BModal v-model="visible"
            size="xl"
            title="Tasks"
            :ok-only="true"
            ok-title="Close">
        <small v-if="analyses.length > 0">
            <table class="table table-hover task-table">
                <thead>
                <tr>
                    <th scope="col" style="width:100px"></th>
                    <th scope="col">Task description</th>
                    <th scope="col" style="width:150px">Actions</th>
                </tr>
                </thead>
                <tbody>
                <TaskStateRow v-for="(analysis, i) in analyses"
                                v-model:analysis="analyses[i]">
                </TaskStateRow>
                </tbody>
            </table>
        </small>
        <div v-if="analyses.length === 0" class="alert alert-info">
            No analysis was triggered for this function and these subjects.
        </div>
    </BModal>
</template>
