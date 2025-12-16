<script setup>

import {cloneDeep} from "lodash";
import {onMounted, ref} from "vue";

import {
    QBtn,
    QBtnGroup,
    QCard,
    QCardSection,
    QLinearProgress
} from 'quasar';

import { useNotify } from "@/utils/notify";
import {managerApiTopographyDestroy} from "@/api";
import {getIdFromUrl} from "@/utils/api";
import {uploadFile} from "topobank/utils/upload";

const { show } = useNotify();

const emit = defineEmits([
    'delete:topography',
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

async function deleteTopography() {
    const topographyId = getIdFromUrl(props.topography.url);
    await managerApiTopographyDestroy({path: {id: topographyId}});
    emit('delete:topography', props.topography.url);
}

</script>

<template>
    <QCard class="q-mb-xs"
           :class="{ 'text-white bg-negative': _error != null }">
        <QCardSection class="flex items-center">
            <h5 class="col-grow q-ma-none">{{ topography.name }}</h5>
            <QBtnGroup v-if="_error != null" flat>
                <QBtn flat text-color="white"
                      @click="deleteTopography">
                    <i class="fa fa-trash"></i>
                </QBtn>
            </QBtnGroup>
        </QCardSection>
        <QCardSection v-if="_error != null">
            <b>Upload failed:</b> {{ _error.message }}
        </QCardSection>
        <QCardSection v-if="_error == null">
            <QLinearProgress :value="_loaded / _total"
                             stripe
                             :animation-speed="300" />
        </QCardSection>
    </QCard>
</template>
