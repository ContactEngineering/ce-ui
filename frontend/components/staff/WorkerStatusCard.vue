<script setup lang="ts">

import {computed} from "vue";
import {BAlert, BBadge, BButton, BCard, BSpinner} from "bootstrap-vue-next";

const props = defineProps({
    // Payload of /staff/api/worker/, or null while the first poll is in flight.
    state: {type: Object, default: null},
    isLoading: {type: Boolean, default: false},
    // Instance-wide task counts from /staff/api/task/summary/.
    summary: {type: Object, default: null}
});

const emit = defineEmits(["refresh"]);

const utilization = computed(() => {
    const total = props.state?.total_concurrency ?? 0;
    if (total === 0) {
        return 0;
    }
    return Math.round(100 * (props.state.active_tasks ?? 0) / total);
});

function formatUptime(seconds: number | null): string {
    if (seconds == null) {
        return "–";
    }
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (days > 0) {
        return `${days} d ${hours} h`;
    }
    if (hours > 0) {
        return `${hours} h ${minutes} min`;
    }
    return `${minutes} min`;
}

</script>

<template>
    <BCard class="mb-3">
        <div class="d-flex align-items-center mb-3">
            <h5 class="mb-0 flex-grow-1">
                Workers
                <BSpinner v-if="isLoading" small class="ms-2"></BSpinner>
            </h5>
            <BButton size="sm" variant="outline-secondary" @click="emit('refresh')">
                <i class="fa fa-rotate-right me-1"></i>Refresh
            </BButton>
        </div>

        <BAlert v-if="state != null && !state.available" :model-value="true"
                variant="warning" class="mb-0">
            <i class="fa fa-triangle-exclamation me-1"></i>
            {{ state.reason }}
        </BAlert>

        <template v-if="state != null && state.available">
            <div class="row g-3 mb-3">
                <div class="col-6 col-lg">
                    <div class="staff-stat">
                        <div class="staff-stat-value">{{ state.num_workers }}</div>
                        <div class="staff-stat-label">Registered workers</div>
                    </div>
                </div>
                <div class="col-6 col-lg">
                    <div class="staff-stat">
                        <div class="staff-stat-value">
                            {{ state.total_concurrency }}
                        </div>
                        <div class="staff-stat-label">
                            Parallel slots
                            <i class="fa fa-circle-info text-muted ms-1"
                               title="Sum of every worker's pool size: the number of tasks that can run at the same time."></i>
                        </div>
                    </div>
                </div>
                <div class="col-6 col-lg">
                    <div class="staff-stat">
                        <div class="staff-stat-value">
                            {{ state.active_tasks }}
                            <span class="staff-stat-suffix">({{ utilization }}%)</span>
                        </div>
                        <div class="staff-stat-label">Busy slots</div>
                    </div>
                </div>
                <div class="col-6 col-lg">
                    <div class="staff-stat">
                        <div class="staff-stat-value">{{ state.reserved_tasks }}</div>
                        <div class="staff-stat-label">Prefetched by workers</div>
                    </div>
                </div>
                <div v-if="summary != null" class="col-6 col-lg">
                    <div class="staff-stat">
                        <div class="staff-stat-value">{{ summary.pending }}</div>
                        <div class="staff-stat-label">Queued tasks</div>
                    </div>
                </div>
                <div v-if="summary != null" class="col-6 col-lg">
                    <div class="staff-stat">
                        <div class="staff-stat-value">
                            {{ summary.failed_last_24h }}
                        </div>
                        <div class="staff-stat-label">Failed (24 h)</div>
                    </div>
                </div>
            </div>

            <div class="progress mb-3" style="height: 6px;">
                <div :style="{width: `${utilization}%`}"
                     :class="utilization >= 90 ? 'bg-danger' : 'bg-primary'"
                     class="progress-bar"
                     role="progressbar"></div>
            </div>

            <div class="table-responsive">
                <table class="table table-sm align-middle mb-0">
                    <thead>
                    <tr>
                        <th scope="col">Machine</th>
                        <th scope="col">Node</th>
                        <th scope="col">Queues</th>
                        <th scope="col">Pool</th>
                        <th class="text-end" scope="col">Slots</th>
                        <th class="text-end" scope="col">Busy</th>
                        <th class="text-end" scope="col">Prefetched</th>
                        <th class="text-end" scope="col">Processed</th>
                        <th class="text-end" scope="col">Uptime</th>
                    </tr>
                    </thead>
                    <tbody>
                    <tr v-for="worker in state.workers" :key="worker.nodename">
                        <td class="fw-semibold">{{ worker.hostname }}</td>
                        <td class="font-monospace small text-muted">
                            {{ worker.nodename }}
                        </td>
                        <td>
                            <BBadge v-for="queue in worker.queues" :key="queue"
                                    class="me-1" variant="light">
                                {{ queue }}
                            </BBadge>
                            <span v-if="worker.queues.length === 0"
                                  class="text-muted">–</span>
                        </td>
                        <td>{{ worker.pool ?? "–" }}</td>
                        <td class="text-end">{{ worker.concurrency }}</td>
                        <td class="text-end">{{ worker.active_tasks }}</td>
                        <td class="text-end">{{ worker.reserved_tasks }}</td>
                        <td class="text-end">{{ worker.processed }}</td>
                        <td class="text-end">{{ formatUptime(worker.uptime) }}</td>
                    </tr>
                    </tbody>
                </table>
            </div>
        </template>
    </BCard>
</template>

<style scoped>
.staff-stat-value {
    font-size: 1.75rem;
    font-weight: 600;
    line-height: 1.1;
}

.staff-stat-suffix {
    font-size: 1rem;
    font-weight: 400;
    color: var(--bs-secondary-color);
}

.staff-stat-label {
    font-size: 0.8rem;
    color: var(--bs-secondary-color);
}
</style>
