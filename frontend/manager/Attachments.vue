<script setup>

import axios from "axios";
import DropZone from '../components/DropZone.vue';
import { ref, computed } from 'vue';

import { BCard, BCardBody, BButton, BButtonGroup, BSpinner, BFormInput, BAlert } from 'bootstrap-vue-next';


const props = defineProps({
    surfaceUrl: String,
    attachments: Array,
    permission: String
});


function onProgress(e) {
    console.log(e);
}

function addFileToList({ id }) {
    axios.get(`/manager/api/file/${id}`)
        .then((response) => {
            props.attachments.push(response.data)
        });
}

function uploadStart({ fileName, fileType }) {
    return axios.post("/manager/api/upload/direct/start/",
        {
            surface: props.surfaceUrl,
            kind: "att",
            file_name: fileName,
            file_type: fileType
        }
    );
}

function uploadDo({ data, file }) {
    if (data.method === 'POST') {
        return axios.postForm(
            data.url,
            { ...data.fields, file: file },
            { onUploadProgress: onProgress }
        );
    } else if (data.method === 'PUT') {
        return axios.put(
            data.url,
            file,
            {
                headers: { 'Content-Type': 'binary/octet-stream' },
                onUploadProgress: onProgress
            }
        );
    } else {
        alert(`Unknown upload method: "${data.method}`);
    }
}

function uploadFinish({ data }) {
    return axios.post("/manager/api/upload/direct/finish/", { file_id: data.id });
}

function handleFileDrop(files) {
    for (const file of files) {
        uploadStart({
            fileName: file.name,
            fileType: file.type
        })
            .then((response) => {
                uploadDo({ data: response.data, file })
                    .then(() => uploadFinish({ data: response.data }))
                    .then(() => {
                        addFileToList({ id: response.data.id });
                    })
            })
            .catch((error) => {
                console.log("error while uploading");
                console.log(error);
            });
    }
}

function formatDateTime(dateTimeString) {
    var date = new Date(dateTimeString);
    return date.toLocaleString();
}

const isEditable = computed(() => {
    return ['edit', 'full'].includes(props.permission);
})

</script>

<template>
    <b-card>
        <template #header>
            <div class="d-flex">
                <h5 class="flex-grow-1">Attachments</h5>
            </div>
        </template>
        <b-card-body>
            <div v-if="!isEditable">
                This digital surface twin does not have file attachments yet.
            </div>
            <drop-zone @files-dropped="handleFileDrop">
                Drop your attachments here or
            </drop-zone>
            <div class="border p-3 rounded mt-5">
                <div v-for="attachment in attachments">
                    <div class="d-flex">
                        <a :href="attachment.file"><i class="fa-solid fa-paperclip me-3"></i>{{ attachment.name }} </a>
                        <span class="ms-auto"> created: {{ formatDateTime(attachment.created) }}</span>
                    </div>
                </div>
            </div>
        </b-card-body>
    </b-card>
</template>
