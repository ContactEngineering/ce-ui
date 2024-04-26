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


const deleteAttachmentIdx = ref(-1);

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

function deleteAttachment(index) {
    if (index < 0 || index >= props.attachments.length) {
        console.error(`The provided index (${index}) is out of range.`);
        return
    }
    const attachment = props.attachments[index];
    axios.delete(attachment.url)
        .then(() => {
            props.attachments.splice(index, 1);
            deleteAttachmentIdx.value = -1;
        })
}

function formatDateTime(dateTimeString) {
    var date = new Date(dateTimeString);
    return date.toLocaleString();
}

const isEditable = computed(() => {
    return ['edit', 'full'].includes(props.permission);
})

const attachmentToDelete = computed(() => {
    if (deleteAttachmentIdx.value >= 0) {
        return props.attachments[deleteAttachmentIdx.value];
    }
    return null;
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
            <drop-zone @files-dropped="handleFileDrop">
                Drop your attachments here or
            </drop-zone>
            <div class=" mt-5">
                <div v-for="(attachment, index) in attachments" :key="attachment.id">
                    <div class="d-flex align-items-center my-1 border rounded px-2 py-1">
                        <a :href="attachment.file"><i class="fa-solid fa-paperclip me-3"></i>{{ attachment.name }}
                        </a>
                        <span class="ms-auto"> created: {{ formatDateTime(attachment.created) }}</span>
                        <b-button size="sm" class="ms-3" title="delete" variant="outline-danger" data
                            data-toggle="modal" data-target="#deleteModal" @click="deleteAttachmentIdx = index">
                            <i class="fa-solid fa-trash"></i> Delete
                        </b-button>
                    </div>
                </div>
                <div v-if="attachments.length == 0">
                    <BAlert :model-value="true" variant="primary">
                        This digital surface twin does not have file attachments yet.
                    </BAlert>
                </div>
            </div>
        </b-card-body>
    </b-card>

    <div id="deleteModal" v-if="deleteAttachmentIdx != -1" class="modal fade" tabindex="-1" role="dialog"
        aria-labelledby="deleteModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="deleteModalLabel">
                        Delete Attachment
                    </h5>
                </div>
                <div class="modal-body">
                    <div class="d-flex flex-column align-items-center">
                        <span class="fw-bold"> This operation will permanently delete the attachment:</span>
                        <span class="fst-italic"> "{{ attachmentToDelete.name }}" </span>
                        <span>The operation cannot be undone!</span>
                    </div>
                </div>
                <div class="modal-footer">
                    <b-button size="xl" variant="outline-secondary" data-dismiss="modal">
                        Cancel
                    </b-button>
                    <b-button size="xl" class="ms-2" variant="outline-danger" data-dismiss="modal"
                        @click="deleteAttachment(deleteAttachmentIdx)">
                        Delete
                    </b-button>
                </div>
            </div>
        </div>
    </div>
</template>
