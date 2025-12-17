<script setup lang="ts">

import { QBtn } from 'quasar';
import {onMounted, ref} from 'vue';

import {managerApiSurfaceRetrieve} from "@/api";

const props = defineProps({
    stage: Number,
    surfaceId: Number
});

const emit = defineEmits(['continue']);

const surface = ref();
const error = ref(false)

onMounted(async () => {
    try {
        const response = await managerApiSurfaceRetrieve({path: {id: props.surfaceId}});
        surface.value = response.data;
    } catch (err) {
        error.value = true;
        console.error(err);
    }
});
</script>
<template>
    <div v-if="props.stage == 0">
        <div v-if="surface && !error" class="q-mt-lg q-pa-md rounded-borders"
             style="background-color: oklch(0.852 0.199 91.936 / 0.4);">
            <h4>
                You are about to publish the digital surface twin: {{ surface.name }}
            </h4>

            By publishing, you create an <strong>immutable copy</strong> of this digital
            twin as a snapshot with all its
            data.
            This snapshot has a version number and a unique URL for citations and it is
            visible and usable to everyone.
        </div>
        <div v-if="error" class="q-mt-lg q-pa-md rounded-borders"
             style="background-color: oklch(0.577 0.245 27.325 / 0.4);">
            <h4>
                Sorry we could not find a digital surface twin with the ID {{
                    surfaceId
                }}
            </h4>
        </div>


        <div v-if="surface && !error" class="flex row justify-end">
            <QBtn @click="emit('continue')" color="primary">
                Continue
            </QBtn>
        </div>
    </div>
</template>
