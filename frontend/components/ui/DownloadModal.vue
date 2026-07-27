<script setup lang="ts">
/**
 * Modal that reports the preparation of a ZIP archive and starts the download once it is ready.
 *
 * Archives of datasets and of analysis results are assembled by a Celery worker, which can take a while for large
 * measurements. This modal drives that flow: it asks the server for an archive, polls the task and shows its progress,
 * and then hands the finished file to the browser.
 *
 * Usage:
 *
 *     <DownloadModal ref="_downloadModal"/>
 *     ...
 *     _downloadModal.value.download(url, {title: "Download dataset"});
 */

import axios from "axios";
import { ref } from "vue";

import { BButton, BModal } from "bootstrap-vue-next";

import { describeRequestError, fetchArchiveUrl, TASK_FAILURE } from "@/utils/download";

import ProgressIndicator from "@/components/ui/ProgressIndicator.vue";

const _visible = ref(false);
const _title = ref("Preparing download");
const _taskState = ref("pe");
const _progress = ref(0);
const _message = ref(null);
const _error = ref(null);

// Set while a download is being prepared. Polling stops when this is cleared, which is how closing the modal aborts the
// wait (the task itself keeps running on the server, so the archive is not wasted).
let _currentRequest = null;

/**
 * Request an archive and download it once it is ready.
 *
 * @param url Endpoint that starts building the archive.
 * @param options.title Heading shown in the modal.
 */
async function download(url: string, options: { title?: string } = {}) {
    const request = {};
    _currentRequest = request;

    _title.value = options.title ?? "Preparing download";
    _taskState.value = "pe";
    _progress.value = 0;
    _message.value = null;
    _error.value = null;
    _visible.value = true;

    try {
        const fileUrl = await fetchArchiveUrl(axios, url, {
            onPoll: (state) => {
                // Ignore a late response from a request the user has already dismissed
                if (_currentRequest !== request) {
                    return;
                }
                _taskState.value = state.task_state;
                _progress.value = state.task_progress ?? 0;
                // The task reports one message per running subtask; the last one is the most recent
                const messages = state.task_messages;
                _message.value = messages != null && messages.length > 0
                    ? messages[messages.length - 1] : null;
            }
        });
        if (_currentRequest !== request) {
            return;
        }
        _visible.value = false;
        window.location.assign(fileUrl);
    } catch (error) {
        if (_currentRequest !== request) {
            return;
        }
        _taskState.value = TASK_FAILURE;
        _error.value = describeRequestError(error);
        // Keep the untruncated failure available for debugging
        console.error("Preparing the archive failed", error);
    } finally {
        if (_currentRequest === request) {
            _currentRequest = null;
        }
    }
}

function cancel() {
    /* Give up on this archive.

       The Celery task keeps running and the finished archive stays in storage until the custodian expires it, but there
       is no way back to it: containers are neither listed nor reused, and the handle only lives in this component. So
       from the user's point of view the archive is gone and asking again rebuilds it from scratch. The same applies when
       the page is unloaded — this is a multi-page application, so navigating anywhere tears the polling down. */
    _currentRequest = null;
    _visible.value = false;
}

defineExpose({
    download
});

</script>

<template>
    <BModal v-model="_visible"
            :title="_title"
            :no-close-on-backdrop="_error == null"
            :no-close-on-esc="_error == null"
            @hide="cancel">
        <div v-if="_error == null">
            <p class="mb-2">
                <span v-if="_taskState === 'pe'">
                    Waiting for a worker to pick up the archive...
                </span>
                <span v-else-if="_message != null">{{ _message }}</span>
                <span v-else>Preparing the archive...</span>
            </p>
            <ProgressIndicator :value="_progress" :state="_taskState"></ProgressIndicator>
            <p class="text-body-secondary mt-3 mb-0">
                <small>
                    The archive is assembled on the server and the download starts automatically once it is ready.
                    Please leave this page open until then &mdash; navigating away or cancelling abandons the archive,
                    and it has to be prepared again from scratch.
                </small>
            </p>
        </div>
        <div v-else class="alert alert-danger mb-0">
            <i class="fa-solid fa-triangle-exclamation me-2"></i>
            The archive could not be prepared: {{ _error }}
        </div>
        <template #footer>
            <BButton variant="secondary" @click="cancel">
                {{ _error == null ? "Cancel download" : "Close" }}
            </BButton>
        </template>
    </BModal>
</template>
