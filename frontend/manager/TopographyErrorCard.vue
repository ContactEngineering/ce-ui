<script lang="ts">

import { QSelect, QBtn, QBtnGroup } from "quasar";

import {
    managerApiTopographyDestroy,
    managerApiTopographyForceInspectCreate,
    managerApiTopographyPartialUpdate
} from "@/api";
import {getIdFromUrl} from "@/utils/api";

export default {
    name: 'topography-error-card',
    components: {
        QSelect, QBtn, QBtnGroup
    },
    emits: [
        'delete:topography',
        'update:topography'
    ],
    props: {
        topography: {
            type: Object,
            default: null
        }
    },
    methods: {
        async deleteTopography() {
            const topographyId = getIdFromUrl(this.topography.url);
            await managerApiTopographyDestroy({path: {id: topographyId}});
            this.$emit('delete:topography', this.topography.url);
        },
        async forceInspect() {
            const topographyId = getIdFromUrl(this.topography.url);
            const response = await managerApiTopographyForceInspectCreate({path: {id: topographyId}});
            this.$emit('update:topography', response.data);
        },
        async dataSourceChanged(value) {
            const topographyId = getIdFromUrl(this.topography.url);
            const response = await managerApiTopographyPartialUpdate({
                path: {id: topographyId},
                body: {'data_source': this.topography.data_source}
            });
            this.$emit('update:topography', response.data);
        }
    },
    computed: {
        channelOptions() {
            if (this.topography === null) {
                return [];
            }

            let options = [];
            for (const [channelIndex, channelName] of this.topography.channel_names.entries()) {
                const [name, unit] = channelName;
                if (unit === null) {
                    options.push({value: channelIndex, label: name});
                } else {
                    options.push({value: channelIndex, label: `${name} (${unit})`});
                }
            }
            return options;
        }
    }
};
</script>

<template>
    <div class="error-card bg-negative text-white q-mb-xs rounded-borders">
        <div class="error-card-header q-pa-sm flex items-center">
            <QBtnGroup flat class="float-right">
                <QBtn flat dense size="sm" text-color="white"
                      @click="forceInspect">
                    <i class="fa fa-refresh"></i>
                </QBtn>
                <QBtn flat dense size="sm" text-color="white"
                      @click="deleteTopography">
                    <i class="fa fa-trash"></i>
                </QBtn>
            </QBtnGroup>
            <div v-if="topography !== null && topography.data_source !== null && topography.channel_names.length > 0"
                 class="q-mr-sm">
                <QSelect :options="channelOptions"
                         v-model="topography.data_source"
                         @update:model-value="dataSourceChanged"
                         emit-value
                         map-options
                         dense
                         dark
                         size="sm"
                         style="min-width: 150px;">
                </QSelect>
            </div>
            <div class="col-grow">
                <h5 class="q-ma-none">{{ topography.name }}</h5>
            </div>
        </div>
        <div class="error-card-body q-pa-sm">
            {{ topography.error }}
        </div>
    </div>
</template>
