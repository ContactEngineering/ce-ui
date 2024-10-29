<script setup>

import axios from "axios";
import {cloneDeep} from "lodash";
import {onMounted, ref} from "vue";

import {
    BButton,
    BButtonGroup,
    BCard,
    BProgress,
    useToastController
} from 'bootstrap-vue-next';

import {uploadFile} from "topobank/utils/upload";

const {show} = useToastController();

const emit = defineEmits([
    'update:topography'
]);

const props = defineProps({
    topography: Object
});

const _error = ref(null);
const _loaded = ref(0);
const _total = ref(1);

function onProgress(e) {
    _loaded.value = e.loaded;
    _total.value = e.total;
}

function emitUpdateTopography() {
    let t = cloneDeep(props.topography);
    // Remove upload instructions
    delete t.file;
    delete t.datafile.upload_instructions;
    // Notify that topography has changed
    emit('update:topography', t);
}

onMounted(() => {
    // Start upload
    uploadFile({
        uploadInstructions: props.topography.datafile.upload_instructions,
        file: props.topography.file,
        onUploadProgress: onProgress
    }).then(response => {
        // Upload successfully finished
        emitUpdateTopography();
    }).catch(error => {
        // Upload failed
        _error.value = error;
        show?.({
            props: {
                title: "Error while uploading",
                body: error.message,
                variant: 'danger'
            }
        });
    });
});

function deleteTopography() {
    axios.delete(props.topography.url);
    this.$emit('delete:topography', props.topography.url);
}

</script>

<template>
    <BCard class="mb-1"
           :class="{ 'text-white bg-danger': _error != null }">
        <template #header>
            <h5 class="float-start">{{ topography.name }}</h5>
            <BButtonGroup v-if="_error != null"
                          size="sm" class="float-end">
                <BButton variant="outline-light"
                         class="text-white float-end ms-2"
                         @click="deleteTopography">
                    <i class="fa fa-trash"></i>
                </BButton>
            </BButtonGroup>
        </template>
        <div v-if="_error != null">
            <b>Upload failed:</b> {{ _error.message }}
            ({{ _error.response.statusText }})
        </div>
        <b-progress v-if="_error == null"
                    show-progress animated
                    :value="_loaded"
                    :max="_total">
        </b-progress>
    </BCard>
</template>
