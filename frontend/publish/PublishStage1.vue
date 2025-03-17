<script setup lang="ts">

import {BButton} from 'bootstrap-vue-next';
import {ref} from 'vue';
import axios from "axios";

const props = defineProps({
    stage: Number,
    surfaceId: Number
});

const emit = defineEmits(['continue']);

const surface = ref();
const error = ref(false)

axios.get(`/manager/api/surface/${props.surfaceId}`).then((response) => {
    surface.value = response.data;
}).catch((response) => {
    error.value = true;
    console.error(response)
});
</script>
<template>
    <div v-if="props.stage == 0">
        <div v-if="surface && !error" class="alert mt-5"
             style="background-color: oklch(0.852 0.199 91.936 / 0.4);">
            <h4>
                You are about to publish the digital surface twin: {{ surface.name }}
            </h4>

            By publishing, you create an <strong>immutable copy</strong> of this digital
            twin as a snapshot with all its
            data.<br>
            This snapshot has a version number and a unique URL for citations and it is
            visible and usable for everyone.
        </div>
        <div v-if="error" class="alert mt-5"
             style="background-color: oklch(0.577 0.245 27.325 / 0.4);">
            <h4>
                Sorry we could not find a digital surface twin with the ID {{
                    surfaceId
                }}
            </h4>
        </div>


        <div v-if="surface && !error" class="d-flex flex-row justify-content-end">
            <BButton @click="emit('continue')" variant="primary">
                Continue
            </BButton>
        </div>
    </div>
</template>
