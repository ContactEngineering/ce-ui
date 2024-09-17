<script setup>

import axios from "axios";
import DropZone from '../components/DropZone.vue';
import { ref, computed } from 'vue';

import { BCard, BCardBody, BButton, BButtonGroup, BSpinner, BFormInput, BAlert, BProgress, BModal, useToast } from 'bootstrap-vue-next';


const props = defineProps({
    fileParentType: String,
    fileParentUrl: String,
    attachments: String,
    permission: String
});

const { show } = useToast()

const deleteAttachmentIdx = ref(-1);
const infoAttachmentIdx = ref(-1);

const uploadIndicator = ref({});

const deleteModal = ref(false)
const infoModal = ref(false)

function addFileToList({ id }) {
    return axios.get(`/manager/api/file/${id}`)
        .then((response) => {
            props.attachments.push(response.data)
        });
}

function uploadStart({ fileName, fileType }) {
    const body = {
        kind: "att",
        file_name: fileName,
        file_type: fileType
    }
    body[props.fileParentType] = props.fileParentUrl
    return axios.post("/manager/api/upload/direct/start/", body);
}

function uploadDo({ data, file }) {
    if (data.method === 'POST') {
        return axios.postForm(
            data.url,
            { ...data.fields, file: file },
            { onUploadProgress: (e) => uploadIndicator.value[data.id].loaded = e.loaded / e.total * 100 }
        );
    } else if (data.method === 'PUT') {
        return axios.put(
            data.url,
            file,
            {
                headers: { 'Content-Type': 'binary/octet-stream' },
                onUploadProgress: (e) => uploadIndicator.value[data.id].loaded = e.loaded / e.total * 100
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
                const fileId = response.data.id;
                uploadIndicator.value[fileId] = { filename: file.name, loaded: 0 };
                uploadDo({ data: response.data, file })
                    .then(() => {
                        uploadFinish({ data: response.data })
                            .then(() => {
                                addFileToList({ id: fileId })
                                    .then(() => delete uploadIndicator.value[fileId]);
                            })
                            .catch((error) => {
                                show?.({ props: { title: "Error while finishing upload", body: "The following Error occured during the upload finilazation: " + error.message, variant: 'danger', pos: 'bottom-right' } });
                                console.error(error);
                                delete uploadIndicator.value[fileId]
                            });
                    })
                    .catch((error) => {
                        show?.({ props: { title: "Error while uploading", body: "The following Error occured during the upload: " + error.message, variant: 'danger', pos: 'bottom-right' } });
                        console.error(error);
                        delete uploadIndicator.value[fileId]
                    });
            })
            .catch((error) => {
                show?.({ props: { title: "Error while initiating upload", body: "The following Error occured during the upload initialization: " + error.message, variant: 'danger', pos: 'bottom-right' } });
                console.error(error);
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
        .catch((error) => {
            show?.({ props: { title: "Error while deleting", body: "The following Error occured during the deletion: " + error.message, variant: 'danger', pos: 'bottom-right' } });
            console.error(error);
        });
}

function formatDateTime(dateTimeString) {
    var date = new Date(dateTimeString);
    return date.toLocaleString();
}

const isEditable = computed(() => {
    return ['edit', 'full'].includes(props.permission);
})

const attachmentToDelete = computed(() => {
    if (deleteAttachmentIdx.value >= 0 && deleteAttachmentIdx.value < props.attachments.length) {
        return props.attachments[deleteAttachmentIdx.value];
    }
    return null;
})

const attachmentToShowInfo = computed(() => {
    if (infoAttachmentIdx.value >= 0 && infoAttachmentIdx.value < props.attachments.length) {
        return props.attachments[infoAttachmentIdx.value];
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
            <drop-zone v-if="isEditable" @files-dropped="handleFileDrop" class="mb-5">
                Drop your attachments here or
            </drop-zone>
            <div>
                <div v-for="(attachment, index) in attachments" :key="attachment.id">
                    <div class="d-flex align-items-center my-1 border rounded px-2 py-1">
                        <a :href="attachment.file"><i class="fa-solid fa-paperclip me-3"></i>{{ attachment.file_name }}
                        </a>
                        <b-button size="sm" class="ms-auto" title="information" variant="outline-info"
                            @click="infoAttachmentIdx = index; infoModal = true;">
                            <i class="fa-solid fa-circle-info"></i> Info
                        </b-button>
                        <b-button v-if="isEditable" size="sm" class="ms-2" title="delete" variant="outline-danger"
                            @click="deleteAttachmentIdx = index; deleteModal = true;">
                            <i class="fa-solid fa-trash"></i> Delete
                        </b-button>
                    </div>
                </div>
                <div v-for="indicator in uploadIndicator">
                    <div class="d-flex align-items-center my-1 border rounded px-2 py-1">
                        <div class="text-muted">
                            <i class="fa-solid fa-paperclip me-3"></i>
                        </div>
                        <b-progress class="flex-grow-1 ms-2" show-progress animated
                            :value="indicator.loaded"></b-progress>
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

    <b-modal v-model="deleteModal" v-if="attachmentToDelete" centered title="Delete Attachment">
        <div class="d-flex flex-column align-items-center">
            <span class="fw-bold"> This operation will permanently delete the attachment:</span>
            <span class="fst-italic"> "{{ attachmentToDelete.file_name }}" </span>
            <span>The operation cannot be undone!</span>
        </div>
        <template #footer>
            <b-button size="xl" variant="outline-secondary" @click="deleteModal = false">
                Cancel
            </b-button>
            <b-button size="xl" class="ms-2" variant="outline-danger"
                @click="deleteModal = false; deleteAttachment(deleteAttachmentIdx)">
                Delete
            </b-button>
        </template>
    </b-modal>

    <b-modal v-model="infoModal" v-if="attachmentToShowInfo" centered ok-only title="Attachment Info">
        <div>
            <div class="row">
                <div class="col-3 fw-bold">
                    Name:
                </div>
                <div class="col">
                    {{ attachmentToShowInfo.file_name }}
                </div>
            </div>
            <div class="row">
                <div class="col-3 fw-bold">
                    Created by:
                </div>
                <div class="col">
                    {{ attachmentToShowInfo.creator_name }}
                </div>
            </div>
            <div class="row">
                <div class="col-3 fw-bold">
                    Created:
                </div>
                <div class="col">
                    {{ formatDateTime(attachmentToShowInfo.created) }}
                </div>
            </div>
            <div class="row">
                <div class="col-3 fw-bold">
                    Updated:
                </div>
                <div class="col">
                    {{ formatDateTime(attachmentToShowInfo.updated) }}
                </div>
            </div>
        </div>
    </b-modal>
</template>
