<script setup lang="ts">

import { ref, computed, onMounted } from 'vue';

import { filesFolderRetrieve, filesManifestDestroy } from "@/api";
import { getIdFromUrl } from "@/utils/api";

import { formatDateTime } from "topobank/utils/formatting";

import {
    QBtn,
    QBanner,
    QIcon,
    QItem,
    QItemSection,
    QItemLabel,
    QList,
    QDialog,
    QCard,
    QCardSection,
    QCardActions,
    ClosePopup
} from 'quasar';

const vClosePopup = ClosePopup;

import { useNotify } from "@/utils/notify";
import UploadModal from '../components/UploadModal.vue';

const props = defineProps({
    attachmentsUrl: String,
    permission: String
});

const attachmentCount = defineModel("attachmentCount", {
    type: Number,
    default: 0
});

const { show } = useNotify();

const attachments = ref({});

const deleteAttachmentKey = ref(null);
const infoAttachmentKey = ref(null);

const deleteModal = ref(false);
const infoModal = ref(false);
const uploadModal = ref(false);

onMounted(() => {
    refreshAttachments();
});

async function refreshAttachments() {
    try {
        const folderId = getIdFromUrl(props.attachmentsUrl);
        const response = await filesFolderRetrieve({ path: { id: folderId } });
        attachments.value = response.data;
        attachmentCount.value = Object.keys(attachments.value).length;
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

function onAttachmentsUploaded(results: any[]) {
    // Add uploaded attachments to the list
    for (const result of results) {
        const manifest = result.manifest;
        attachments.value[manifest.filename] = manifest;
    }
    attachmentCount.value = Object.keys(attachments.value).length;
}

async function deleteAttachment(key) {
    const attachment = attachments.value[key];
    try {
        const manifestId = getIdFromUrl(attachment.url);
        await filesManifestDestroy({ path: { id: manifestId } });
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
        <!-- Upload button -->
        <div v-if="isEditable" class="q-mb-md">
            <QBtn color="primary"
                  icon="attach_file"
                  label="Add attachment"
                  @click="uploadModal = true" />
        </div>

        <QBanner v-if="attachmentCount === 0"
                 class="bg-grey-2 text-grey-8">
            <template #avatar>
                <QIcon name="info" color="grey-6" />
            </template>
            No attachments yet.
        </QBanner>

        <QList v-if="attachmentCount > 0" bordered separator class="rounded-borders">
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
        </QList>
    </div>

    <!-- Upload Modal -->
    <UploadModal v-model="uploadModal"
                 mode="attachment"
                 :target-url="attachmentsUrl"
                 @uploaded="onAttachmentsUploaded" />

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
