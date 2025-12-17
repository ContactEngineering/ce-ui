<script setup lang="ts">

import DropZone from '../components/DropZone.vue';
import {ref, computed, onMounted} from 'vue';

import {filesFolderRetrieve, filesManifestRetrieve, filesManifestDestroy} from "@/api";
import {getIdFromUrl} from "@/utils/api";

import {formatDateTime} from "topobank/utils/formatting";
import {uploadFile, createFileManifest} from "topobank/utils/upload";

import {
    QBtn,
    QBanner,
    QIcon,
    QItem,
    QItemSection,
    QItemLabel,
    QLinearProgress,
    QList,
    QDialog,
    QCard,
    QCardSection,
    QCardActions,
    QSeparator
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
    <div>
        <DropZone v-if="isEditable" @files-dropped="handleFileDrop" class="q-mb-md">
            Drop your attachments here or
        </DropZone>

        <QBanner v-if="attachmentCount === 0 && Object.keys(uploadIndicator).length === 0"
                 class="bg-grey-2 text-grey-8">
            <template #avatar>
                <QIcon name="info" color="grey-6" />
            </template>
            No attachments yet.
        </QBanner>

        <QList v-if="attachmentCount > 0 || Object.keys(uploadIndicator).length > 0" bordered separator class="rounded-borders">
            <!-- Existing attachments -->
            <QItem v-for="[key, value] in Object.entries(attachments)" :key="value.id">
                <QItemSection avatar>
                    <QIcon name="attach_file" color="grey-7" />
                </QItemSection>
                <QItemSection>
                    <QItemLabel>
                        <a :href="value.file" class="text-primary">{{ value.filename }}</a>
                    </QItemLabel>
                    <QItemLabel caption>
                        {{ formatDateTime(value.created) }}
                    </QItemLabel>
                </QItemSection>
                <QItemSection side>
                    <div class="row no-wrap q-gutter-xs">
                        <QBtn flat dense round icon="info" color="grey-7"
                              @click="infoAttachmentKey = key; infoModal = true;" />
                        <QBtn v-if="isEditable" flat dense round icon="delete" color="negative"
                              @click="deleteAttachmentKey = key; deleteModal = true;" />
                    </div>
                </QItemSection>
            </QItem>

            <!-- Upload progress indicators -->
            <QItem v-for="indicator in uploadIndicator" :key="indicator.filename">
                <QItemSection avatar>
                    <QIcon name="upload_file" color="grey-5" />
                </QItemSection>
                <QItemSection>
                    <QItemLabel class="text-grey">{{ indicator.filename }}</QItemLabel>
                    <QLinearProgress :value="indicator.loaded / 100"
                                     color="primary"
                                     class="q-mt-xs" />
                </QItemSection>
            </QItem>
        </QList>
    </div>

    <!-- Delete confirmation dialog -->
    <QDialog v-model="deleteModal">
        <QCard v-if="attachmentToDelete" style="min-width: 350px">
            <QCardSection>
                <div class="text-h6">Delete attachment</div>
            </QCardSection>
            <QCardSection class="q-pt-none">
                <p>This will permanently delete:</p>
                <p class="text-weight-medium q-my-sm">"{{ attachmentToDelete.filename }}"</p>
                <p class="text-caption text-negative">This cannot be undone.</p>
            </QCardSection>
            <QCardActions align="right">
                <QBtn flat label="Cancel" v-close-popup />
                <QBtn color="negative" label="Delete"
                      @click="deleteModal = false; deleteAttachment(deleteAttachmentKey)" />
            </QCardActions>
        </QCard>
    </QDialog>

    <!-- Info dialog -->
    <QDialog v-model="infoModal">
        <QCard v-if="attachmentToShowInfo" style="min-width: 350px">
            <QCardSection>
                <div class="text-h6">Attachment details</div>
            </QCardSection>
            <QCardSection class="q-pt-none">
                <QList dense>
                    <QItem>
                        <QItemSection>
                            <QItemLabel caption>Filename</QItemLabel>
                            <QItemLabel>{{ attachmentToShowInfo.filename }}</QItemLabel>
                        </QItemSection>
                    </QItem>
                    <QItem>
                        <QItemSection>
                            <QItemLabel caption>Uploaded by</QItemLabel>
                            <QItemLabel>{{ attachmentToShowInfo.uploaded_by }}</QItemLabel>
                        </QItemSection>
                    </QItem>
                    <QItem>
                        <QItemSection>
                            <QItemLabel caption>Created</QItemLabel>
                            <QItemLabel>{{ formatDateTime(attachmentToShowInfo.created) }}</QItemLabel>
                        </QItemSection>
                    </QItem>
                    <QItem>
                        <QItemSection>
                            <QItemLabel caption>Updated</QItemLabel>
                            <QItemLabel>{{ formatDateTime(attachmentToShowInfo.updated) }}</QItemLabel>
                        </QItemSection>
                    </QItem>
                </QList>
            </QCardSection>
            <QCardActions align="right">
                <QBtn flat label="Close" v-close-popup />
            </QCardActions>
        </QCard>
    </QDialog>
</template>
