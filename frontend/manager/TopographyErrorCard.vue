<script lang="ts">

import {BFormSelect} from "bootstrap-vue-next";

import {
    managerApiTopographyDestroy,
    managerApiTopographyForceInspectCreate,
    managerApiTopographyPartialUpdate
} from "@/api";
import {getIdFromUrl} from "@/utils/api";

export default {
    name: 'topography-error-card',
    components: {
        BFormSelect
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
                    options.push({value: channelIndex, text: name});
                } else {
                    options.push({value: channelIndex, text: `${name} (${unit})`});
                }
            }
            return options;
        }
    }
};
</script>

<template>
    <div class="card text-white bg-danger mb-1">
        <div class="card-header">
            <div class="btn-group btn-group-sm float-end">
                <button class="btn btn-outline-light text-white"
                        @click="forceInspect">
                    <i class="fa fa-refresh"></i>
                </button>
                <button class="btn btn-outline-light text-white"
                        @click="deleteTopography">
                    <i class="fa fa-trash"></i>
                </button>
            </div>
            <div v-if="topography !== null && topography.data_source !== null && topography.channel_names.length > 0"
                 class="input-group-sm float-start me-2">
                <BFormSelect :options="channelOptions"
                               v-model="topography.data_source"
                               @change="dataSourceChanged">
                </BFormSelect>
            </div>
            <div>
                <h5 class="d-inline">{{ topography.name }}</h5>
            </div>
        </div>
        <div class="card-body">
            {{ topography.error }}
        </div>
    </div>
</template>
