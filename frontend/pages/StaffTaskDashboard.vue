<script setup lang="ts">

import axios from "axios";
import {onBeforeUnmount, onMounted, ref, watch} from "vue";

import {
    BAlert,
    BButton,
    BButtonToolbar,
    BFormCheckbox,
    BFormInput,
    BFormSelect,
    BInputGroup,
    BOverlay,
    BPagination
} from "bootstrap-vue-next";

import TaskStateBadge from "@/components/staff/TaskStateBadge.vue";
import WorkerStatusCard from "@/components/staff/WorkerStatusCard.vue";
import SortableTh from "@/components/staff/SortableTh.vue";
import {formatDuration} from "@/utils/formatting";
import {
    formatBytes,
    formatTimestamp,
    usePaginatedList
} from "@/utils/paginatedList";

const props = defineProps({
    taskApiUrl: {type: String, default: "/staff/api/task/"},
    workerApiUrl: {type: String, default: "/staff/api/worker/"},
    summaryApiUrl: {type: String, default: "/staff/api/task/summary/"},
    // The server caches the worker inspection for a few seconds, so polling
    // this fast does not multiply broker round trips.
    refreshInterval: {type: Number, default: 5000}
});

const stateFilterChoices = [
    {text: "All states", value: ""},
    {text: "Running", value: "st"},
    {text: "Pending", value: "pe"},
    {text: "Waiting for dependencies", value: "pd"},
    {text: "Retrying", value: "re"},
    {text: "Success", value: "su"},
    {text: "Failure", value: "fa"},
    {text: "Not run", value: "no"}
];

const stateFilter = ref<string>("");
const autoRefresh = ref<boolean>(true);
const workerState = ref<any>(null);
const workersLoading = ref<boolean>(false);
const summary = ref<any>(null);

const {
    items, count, currentPage, pageSize, isLoading, errorMessage,
    searchTerm, ordering, load, goToPage, sortBy
} = usePaginatedList(props.taskApiUrl, {
    pageSize: 25,
    // Leave the ordering unset so the server default applies: running tasks
    // first, so the table reads as a picture of the current load.
    ordering: null,
    extraParams: () => stateFilter.value === "" ? {} : {state: stateFilter.value}
});

let refreshTimer: ReturnType<typeof setInterval> | null = null;

function loadWorkers(force: boolean = false) {
    workersLoading.value = true;
    axios.get(force ? `${props.workerApiUrl}?refresh=1` : props.workerApiUrl)
        .then(response => {
            workerState.value = response.data;
        })
        .catch(error => {
            workerState.value = {
                available: false,
                reason: error.response?.data?.detail ?? String(error),
                workers: []
            };
        })
        .finally(() => {
            workersLoading.value = false;
        });
}

function loadSummary() {
    axios.get(props.summaryApiUrl)
        .then(response => {
            summary.value = response.data;
        })
        .catch(() => {
            summary.value = null;
        });
}

function refreshAll(force: boolean = false) {
    loadWorkers(force);
    loadSummary();
    load((currentPage.value - 1) * pageSize.value);
}

function startAutoRefresh() {
    stopAutoRefresh();
    refreshTimer = setInterval(() => {
        // Do not poll while the tab is in the background.
        if (!document.hidden) {
            refreshAll();
        }
    }, props.refreshInterval);
}

function stopAutoRefresh() {
    if (refreshTimer != null) {
        clearInterval(refreshTimer);
        refreshTimer = null;
    }
}

watch(autoRefresh, enabled => enabled ? startAutoRefresh() : stopAutoRefresh());
watch(stateFilter, () => load());

onMounted(() => {
    refreshAll();
    startAutoRefresh();
});

onBeforeUnmount(stopAutoRefresh);

/** Drop any explicit column sort and fall back to the server's ordering. */
function resetOrdering() {
    ordering.value = null;
    load();
}

/**
 * Label for the user who created a task.
 *
 * `name` is not guaranteed to be a usable label: it can be empty, or
 * whitespace-only for accounts with neither a name nor a first/last name (the
 * anonymous user, for instance). Those must fall back to the username rather
 * than render an empty cell, which reads as "this task has no user".
 */
function userLabel(user: any): string {
    if (user == null) {
        return "–";
    }
    return user.name?.trim() || user.username?.trim() || "–";
}

/** Link to the UI page for a task's subject, if it has one we can link to. */
function subjectHref(subject: any): string | null {
    if (subject == null || subject.id == null) {
        return null;
    }
    if (subject.type === "measurement") {
        return `/ui/topography/${subject.id}/`;
    }
    if (subject.type === "dataset") {
        return `/ui/dataset-detail/${subject.id}/`;
    }
    return null;
}

</script>

<template>
    <div class="d-flex align-items-center mb-3">
        <BFormCheckbox v-model="autoRefresh" switch>
            Auto-refresh
        </BFormCheckbox>
    </div>

    <WorkerStatusCard :is-loading="workersLoading" :state="workerState"
                      :summary="summary"
                      @refresh="refreshAll(true)"></WorkerStatusCard>

    <BAlert v-if="errorMessage != null" :model-value="true" variant="danger">
        {{ errorMessage }}
    </BAlert>

    <BButtonToolbar class="mb-3 gap-2 flex-wrap">
        <BInputGroup class="flex-grow-1" style="max-width: 28rem;">
            <template #prepend>
                <span class="input-group-text"><i class="fa fa-search"></i></span>
            </template>
            <BFormInput v-model="searchTerm"
                        placeholder="Search by workflow, subject, user, error or task ID"
                        type="search">
            </BFormInput>
        </BInputGroup>
        <BInputGroup prepend="State" style="max-width: 20rem;">
            <BFormSelect v-model="stateFilter" :disabled="isLoading"
                         :options="stateFilterChoices">
            </BFormSelect>
        </BInputGroup>
        <BInputGroup prepend="Page size" style="max-width: 14rem;">
            <BFormSelect v-model="pageSize" :disabled="isLoading"
                         :options="[10, 25, 50, 100]">
            </BFormSelect>
        </BInputGroup>
        <BButton v-if="ordering != null" size="sm" variant="outline-secondary"
                 @click="resetOrdering">
            <i class="fa fa-arrow-rotate-left me-1"></i>Running first
        </BButton>
        <div class="d-flex align-items-center text-muted ms-auto">
            {{ count }} task{{ count === 1 ? "" : "s" }}
        </div>
    </BButtonToolbar>

    <BOverlay :show="isLoading">
        <div class="table-responsive">
            <table class="table table-sm table-hover align-middle">
                <thead>
                <tr>
                    <SortableTh :ordering="ordering" field="task_state" @sort="sortBy">
                        State
                    </SortableTh>
                    <SortableTh :ordering="ordering" field="workflow_name"
                                @sort="sortBy">
                        Workflow
                    </SortableTh>
                    <th scope="col">Subject</th>
                    <th scope="col">User</th>
                    <th scope="col">Queue</th>
                    <SortableTh :ordering="ordering" field="task_submission_time"
                                @sort="sortBy">
                        Submitted
                    </SortableTh>
                    <SortableTh :ordering="ordering" field="task_start_time"
                                @sort="sortBy">
                        Started
                    </SortableTh>
                    <th class="text-end" scope="col">Duration</th>
                    <SortableTh :ordering="ordering" field="task_memory" numeric
                                @sort="sortBy">
                        Memory
                    </SortableTh>
                </tr>
                </thead>
                <tbody>
                <tr v-for="task in items" :key="task.id"
                    :class="{'table-primary': task.is_running,
                             'table-danger': task.task_state === 'fa'}">
                    <td>
                        <TaskStateBadge :label="task.task_state_display"
                                        :state="task.task_state"></TaskStateBadge>
                    </td>
                    <td>
                        <span class="font-monospace small">
                            {{ task.workflow_name }}
                        </span>
                        <div v-if="task.name" class="small text-muted">
                            {{ task.name }}
                        </div>
                        <div v-if="task.task_error"
                             :title="task.task_error"
                             class="small text-danger text-truncate"
                             style="max-width: 22rem;">
                            {{ task.task_error }}
                        </div>
                    </td>
                    <td>
                        <a v-if="subjectHref(task.subject) != null"
                           :href="subjectHref(task.subject)">
                            {{ task.subject.name }}
                        </a>
                        <span v-else-if="task.subject != null">
                            {{ task.subject.name }}
                        </span>
                        <span v-else class="text-muted">–</span>
                        <div v-if="task.subject != null" class="small text-muted">
                            {{ task.subject.type }}
                        </div>
                    </td>
                    <td class="small">
                        {{ userLabel(task.created_by) }}
                    </td>
                    <td class="small">{{ task.queue ?? "–" }}</td>
                    <td class="small">
                        {{ formatTimestamp(task.task_submission_time) }}
                    </td>
                    <td class="small">{{ formatTimestamp(task.task_start_time) }}</td>
                    <td class="text-end small">
                        {{ formatDuration(task.duration) }}
                        <i v-if="task.is_running" class="fa fa-hourglass-half ms-1"
                           title="Still running; elapsed time so far"></i>
                    </td>
                    <td class="text-end small">{{ formatBytes(task.task_memory) }}</td>
                </tr>
                <tr v-if="!isLoading && items.length === 0">
                    <td class="text-center text-muted py-4" colspan="9">
                        No tasks match this search.
                    </td>
                </tr>
                </tbody>
            </table>
        </div>

        <BPagination :disabled="isLoading" :limit="9" :model-value="currentPage"
                     :per-page="pageSize" :total-rows="count"
                     @update:model-value="goToPage">
        </BPagination>
    </BOverlay>
</template>
