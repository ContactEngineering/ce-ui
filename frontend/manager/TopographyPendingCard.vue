<script lang="ts">

import { QSpinner, QBtn, QBtnGroup } from 'quasar';

import {
    managerApiTopographyDestroy,
    managerApiTopographyForceInspectCreate
} from "@/api";
import {getIdFromUrl} from "@/utils/api";

export default {
    name: 'topography-pending-card',
    components: {
        QSpinner, QBtn, QBtnGroup
    },
    emits: [
        'delete:topography',
        'update:topography'
    ],
    props: {
        url: String,  // API url
        name: String,  // Used for the title of the card
        taskState: String  // State of task, 'pe', 'st', etc
    },
    methods: {
        async deleteTopography() {
            const topographyId = getIdFromUrl(this.url);
            await managerApiTopographyDestroy({path: {id: topographyId}});
            this.$emit('delete:topography', this.url);
        },
        async forceInspect() {
            const topographyId = getIdFromUrl(this.url);
            const response = await managerApiTopographyForceInspectCreate({path: {id: topographyId}});
            this.$emit('update:topography', response.data);
        }
    }
};
</script>

<template>
    <div class="pending-card q-mb-xs border rounded-borders">
        <div class="pending-card-header q-pa-sm flex items-center">
            <QBtnGroup flat class="float-right">
                <QBtn flat dense size="sm" icon="refresh"
                      @click="forceInspect" />
                <QBtn flat dense size="sm" icon="delete"
                      @click="deleteTopography" />
            </QBtnGroup>
            <div class="col-grow">
                <h5 class="q-ma-none">{{ name }}</h5>
            </div>
        </div>
        <div v-if="taskState !== 'st'"
             class="pending-card-body q-pa-sm">
            <QSpinner size="1rem" class="q-mr-sm" />
            Waiting for data file inspection to start...
        </div>
        <div v-if="taskState === 'st'"
             class="pending-card-body q-pa-sm">
            <QSpinner size="1rem" class="q-mr-sm" />
            Inspecting data file and applying filters...
        </div>
    </div>
</template>
