<script setup lang="ts">

import DropZone from '../components/DropZone.vue';
import {ref, computed, onMounted} from 'vue';

import {filesFolderRetrieve, filesManifestRetrieve, filesManifestDestroy} from "@/api";
import {getIdFromUrl} from "@/utils/api";

import {formatDateTime} from "topobank/utils/formatting";
import {uploadFile, createFileManifest} from "topobank/utils/upload";

import {
    QCard,
    QCardSection,
    QBtn,
    QBanner,
    QLinearProgress,
    QDialog
} from 'quasar';

import { useNotify } from "@/utils/notify";

const props = defineProps({
    attachmentsUrl: String,
    permission: String
});

const attachmentCount = defineModel("attachmentCount",{
    type: Number,
    default: 0
});


const { show } = useNotify();

const attachments = ref({});

const deleteAttachmentKey = ref(null);
const infoAttachmentKey = ref(null);

const uploadIndicator = ref({});

const deleteModal = ref(false);
const infoModal = ref(false);

onMounted(() => {
    refreshAttachments();
});

async function refreshAttachments() {
    try {
        const folderId = getIdFromUrl(props.attachmentsUrl);
        const response = await filesFolderRetrieve({path: {id: folderId}});
        attachments.value = response.data;
        attachmentCount.value = Object.keys(attachments.value).length; // Update the attachment count
    } catch (error: any) {
        show?.({
            props: {
                title: "Error while listing attachments",
                body: error.message,
                variant: "danger"
            }
        });
    }
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
            }).then(async response => {
                attachments.value[manifest.filename] = manifest;
                attachmentCount.value = Object.keys(attachments.value).length;
                uploadIndicator.value = {};
                // We need to fetch the manifest information again to have a link to
                // the file
                try {
                    const manifestId = getIdFromUrl(manifest.url);
                    const manifestResponse = await filesManifestRetrieve({path: {id: manifestId}});
                    attachments.value[manifest.filename] = manifestResponse.data;
                } catch (error: any) {
                    show?.({
                        props: {
                            title: "Error while fetching attachment",
                            body: error.message,
                            variant: 'danger'
                        }
                    });
                    console.error(error);
                }
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

async function deleteAttachment(key) {
    const attachment = attachments.value[key];
    try {
        const manifestId = getIdFromUrl(attachment.url);
        await filesManifestDestroy({path: {id: manifestId}});
        delete attachments.value[key];
        attachmentCount.value = Object.keys(attachments.value).length;
        deleteAttachmentKey.value = null;
    } catch (error: any) {
        show?.({
            props: {
                title: "Error while deleting",
                body: error.message,
                variant: 'danger'
            }
        });
        console.error(error);
    }
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
    <QCard>
        <QCardSection class="flex items-center">
            <h5 class="col-grow q-ma-none">Attachments</h5>
        </QCardSection>
        <QCardSection>
            <DropZone v-if="isEditable" @files-dropped="handleFileDrop" class="q-mb-lg">
                Drop your attachments here or
            </DropZone>
            <div>
                <div v-for="[key, value] in Object.entries(attachments)"
                     :key="value.id">
                    <div
                        class="flex items-center q-my-xs border rounded q-px-sm q-py-xs">
                        <a :href="value.file">
                            <q-icon name="attach_file" class="q-mr-md" />{{ value.filename }}
                        </a>
                        <QBtn size="sm" class="q-ml-auto" title="information"
                              flat color="info" icon="info"
                              @click="infoAttachmentKey = key; infoModal = true;"
                              label="Info" />
                        <QBtn v-if="isEditable" size="sm" class="q-ml-sm"
                              title="delete" flat color="negative" icon="delete"
                              @click="deleteAttachmentKey = key; deleteModal = true;"
                              label="Delete" />
                    </div>
                </div>
                <div v-for="indicator in uploadIndicator" :key="indicator.filename">
                    <div
                        class="flex items-center q-my-xs border rounded q-px-sm q-py-xs">
                        <div class="text-grey">
                            <q-icon name="attach_file" class="q-mr-md" />
                        </div>
                        <QLinearProgress class="col-grow q-ml-sm"
                                         :value="indicator.loaded / 100"
                                         stripe
                                         :animation-speed="300" />
                    </div>
                </div>
                <div v-if="attachmentCount == 0">
                    <QBanner class="bg-primary text-white">
                        This digital surface twin does not have file attachments yet.
                    </QBanner>
                </div>
            </div>
        </QCardSection>
    </QCard>

    <QDialog v-model="deleteModal">
        <QCard v-if="attachmentToDelete" style="min-width: 350px">
            <QCardSection class="row items-center">
                <div class="text-h6">Delete Attachment</div>
            </QCardSection>
            <QCardSection class="flex column items-center">
                <span class="text-weight-bold"> This operation will permanently delete the attachment:</span>
                <span class="text-italic"> "{{ attachmentToDelete.filename }}" </span>
                <span>The operation cannot be undone!</span>
            </QCardSection>
            <QCardSection class="flex justify-end q-gutter-sm">
                <QBtn flat label="Cancel"
                      @click="deleteModal = false" />
                <QBtn color="negative" label="Delete"
                      @click="deleteModal = false; deleteAttachment(deleteAttachmentKey)" />
            </QCardSection>
        </QCard>
    </QDialog>

    <QDialog v-model="infoModal">
        <QCard v-if="attachmentToShowInfo" style="min-width: 350px">
            <QCardSection class="row items-center">
                <div class="text-h6">Attachment Info</div>
            </QCardSection>
            <QCardSection>
                <div class="row q-mb-sm">
                    <div class="col-3 text-weight-bold">
                        Name:
                    </div>
                    <div class="col">
                        {{ attachmentToShowInfo.filename }}
                    </div>
                </div>
                <div class="row q-mb-sm">
                    <div class="col-3 text-weight-bold">
                        Uploaded by:
                    </div>
                    <div class="col">
                        {{ attachmentToShowInfo.uploaded_by }}
                    </div>
                </div>
                <div class="row q-mb-sm">
                    <div class="col-3 text-weight-bold">
                        Created:
                    </div>
                    <div class="col">
                        {{ formatDateTime(attachmentToShowInfo.created) }}
                    </div>
                </div>
                <div class="row q-mb-sm">
                    <div class="col-3 text-weight-bold">
                        Updated:
                    </div>
                    <div class="col">
                        {{ formatDateTime(attachmentToShowInfo.updated) }}
                    </div>
                </div>
            </QCardSection>
            <QCardSection class="flex justify-end">
                <QBtn flat label="OK" v-close-popup />
            </QCardSection>
        </QCard>
    </QDialog>
</template>
