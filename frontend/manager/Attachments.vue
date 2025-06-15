<script setup lang="ts">

import axios from "axios";
import DropZone from '../components/DropZone.vue';
import {ref, computed, onMounted} from 'vue';

import {formatDateTime} from "topobank/utils/formatting";
import {uploadFile, createFileManifest} from "topobank/utils/upload";

import {
    BCard,
    BCardBody,
    BButton,
    BAlert,
    BProgress,
    BModal,
    useToastController
} from 'bootstrap-vue-next';


const props = defineProps({
    attachmentsUrl: String,
    permission: String
});

const attachmentCount = defineModel("attachmentCount",{
    type: Number,
    default: 0
});


const {show} = useToastController();

const attachments = ref({});

const deleteAttachmentKey = ref(null);
const infoAttachmentKey = ref(null);

const uploadIndicator = ref({});

const deleteModal = ref(false);
const infoModal = ref(false);

onMounted(() => {
    refreshAttachments();
});

function refreshAttachments() {
    axios.get(props.attachmentsUrl).then(response => {
        attachments.value = response.data;
        attachmentCount.value = Object.keys(attachments.value).length; // Update the attachment count
    }).catch(error => {
        show?.({
            props: {
                title: "Error while listing attachments",
                body: error.message,
                variant: "danger"
            }
        });
    });
}

function handleFileDrop(files) {
    for (const file of files) {
        createFileManifest({
            folderUrl: props.attachmentsUrl, fileName: file.name
        }).then(response => {
            const manifest = response.data;
            uploadIndicator.value[manifest.id] = {
                filename: manifest.filename,
                loaded: 0
            };
            uploadFile({
                uploadInstructions: manifest.upload_instructions,
                file: file,
                onUploadProgress: e => uploadIndicator.value[manifest.id].loaded = e.loaded / e.total * 100
            }).then(response => {
                attachments.value[manifest.filename] = manifest;
                uploadIndicator.value = {};
                // We need to fetch the manifest information again to have a link to
                // the file
                axios.get(manifest.url).then(response => {
                    attachments.value[manifest.filename] = response.data;
                }).catch(error => {
                    show?.({
                        props: {
                            title: "Error while fetching attachment",
                            body: error.message,
                            variant: 'danger'
                        }
                    });
                    console.error(error);
                });
            }).catch(error => {
                show?.({
                    props: {
                        title: "Error while uploading",
                        body: error.message,
                        variant: 'danger'
                    }
                });
                console.error(error);
                delete uploadIndicator.value[fileId];
            });
        }).catch((error) => {
            show?.({
                props: {
                    title: "Error while initiating upload",
                    body: error.message,
                    variant: 'danger'
                }
            });
            console.error(error);
        });
    }
}

function deleteAttachment(key) {
    const attachment = attachments.value[key];
    axios.delete(attachment.url)
        .then(() => {
            delete attachments.value[key];
            deleteAttachmentKey.value = null;
        })
        .catch((error) => {
            show?.({
                props: {
                    title: "Error while deleting",
                    body: error.message,
                    variant: 'danger'
                }
            });
            console.error(error);
        });
}

const isEditable = computed(() => {
    return ['edit', 'full'].includes(props.permission);
});

const attachmentToDelete = computed(() => {
    if (deleteAttachmentKey.value != null) {
        return attachments.value[deleteAttachmentKey.value];
    }
    return null;
});

const attachmentToShowInfo = computed(() => {
    if (infoAttachmentKey.value != null) {
        return attachments.value[infoAttachmentKey.value];
    }
    return null;
});

</script>
<template>
    <BCard>
        <template #header>
            <div class="d-flex">
                <h5 class="flex-grow-1">Attachments</h5>
            </div>
        </template>
        <BCardBody>
            <DropZone v-if="isEditable" @files-dropped="handleFileDrop" class="mb-5">
                Drop your attachments here or
            </DropZone>
            <div>
                <div v-for="[key, value] in Object.entries(attachments)"
                     :key="value.id">
                    <div
                        class="d-flex align-items-center my-1 border rounded px-2 py-1">
                        <a :href="value.file"><i
                            class="fa-solid fa-paperclip me-3"></i>{{
                                value.filename
                            }}
                        </a>
                        <BButton size="sm" class="ms-auto" title="information"
                                 variant="outline-info"
                                 @click="infoAttachmentKey = key; infoModal = true;">
                            <i class="fa-solid fa-circle-info"></i> Info
                        </BButton>
                        <BButton v-if="isEditable" size="sm" class="ms-2"
                                 title="delete" variant="outline-danger"
                                 @click="deleteAttachmentKey = key; deleteModal = true;">
                            <i class="fa-solid fa-trash"></i> Delete
                        </BButton>
                    </div>
                </div>
                <div v-for="indicator in uploadIndicator">
                    <div
                        class="d-flex align-items-center my-1 border rounded px-2 py-1">
                        <div class="text-muted">
                            <i class="fa-solid fa-paperclip me-3"></i>
                        </div>
                        <b-progress class="flex-grow-1 ms-2" show-progress animated
                                    :value="indicator.loaded"></b-progress>
                    </div>
                </div>
                <div v-if="attachmentCount == 0">
                    <BAlert :model-value="true" variant="primary">
                        This digital surface twin does not have file attachments yet.
                    </BAlert>
                </div>
            </div>
        </BCardBody>
    </BCard>

    <BModal v-model="deleteModal" v-if="attachmentToDelete" centered
            title="Delete Attachment">
        <div class="d-flex flex-column align-items-center">
            <span class="fw-bold"> This operation will permanently delete the attachment:</span>
            <span class="fst-italic"> "{{ attachmentToDelete.filename }}" </span>
            <span>The operation cannot be undone!</span>
        </div>
        <template #footer>
            <BButton size="xl" variant="outline-secondary"
                     @click="deleteModal = false">
                Cancel
            </BButton>
            <BButton size="xl" class="ms-2" variant="outline-danger"
                     @click="deleteModal = false; deleteAttachment(deleteAttachmentKey)">
                Delete
            </BButton>
        </template>
    </BModal>

    <BModal v-model="infoModal" v-if="attachmentToShowInfo" centered ok-only
            title="Attachment Info">
        <div>
            <div class="row">
                <div class="col-3 fw-bold">
                    Name:
                </div>
                <div class="col">
                    {{ attachmentToShowInfo.filename }}
                </div>
            </div>
            <div class="row">
                <div class="col-3 fw-bold">
                    Uploaded by:
                </div>
                <div class="col">
                    {{ attachmentToShowInfo.uploaded_by }}
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
    </BModal>
</template>
