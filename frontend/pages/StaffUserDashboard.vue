<script setup lang="ts">

import {onMounted} from "vue";

import {
    BAlert,
    BButtonToolbar,
    BFormInput,
    BFormSelect,
    BInputGroup,
    BOverlay,
    BPagination
} from "bootstrap-vue-next";

import SortableTh from "@/components/staff/SortableTh.vue";
import TermsBadge from "@/components/staff/TermsBadge.vue";
import {formatTimestamp, usePaginatedList} from "@/utils/paginatedList";

const props = defineProps({
    apiUrl: {type: String, default: "/staff/api/user/"}
});

const {
    items, count, currentPage, pageSize, isLoading, errorMessage,
    searchTerm, ordering, load, goToPage, sortBy
} = usePaginatedList(props.apiUrl, {pageSize: 25, ordering: "-date_joined"});

onMounted(() => load());

</script>

<template>
    <BAlert v-if="errorMessage != null" :model-value="true" variant="danger">
        {{ errorMessage }}
    </BAlert>

    <BButtonToolbar class="mb-3 gap-2 flex-wrap">
        <BInputGroup class="flex-grow-1" style="max-width: 28rem;">
            <template #prepend>
                <span class="input-group-text"><i class="fa fa-search"></i></span>
            </template>
            <BFormInput v-model="searchTerm"
                        placeholder="Search by name, username, email or ORCID iD"
                        type="search">
            </BFormInput>
        </BInputGroup>
        <BInputGroup prepend="Page size" style="max-width: 14rem;">
            <BFormSelect v-model="pageSize" :disabled="isLoading"
                         :options="[10, 25, 50, 100]">
            </BFormSelect>
        </BInputGroup>
    </BButtonToolbar>

    <BOverlay :show="isLoading">
        <div class="table-responsive">
            <table class="table table-sm table-hover align-middle">
                <thead>
                <tr>
                    <SortableTh :ordering="ordering" field="name" @sort="sortBy">
                        Name
                    </SortableTh>
                    <SortableTh :ordering="ordering" field="username" @sort="sortBy">
                        Username
                    </SortableTh>
                    <SortableTh :ordering="ordering" field="orcid" @sort="sortBy">
                        ORCID iD
                    </SortableTh>
                    <th scope="col">Terms of use</th>
                    <SortableTh :ordering="ordering" field="date_joined"
                                @sort="sortBy">
                        Registered
                    </SortableTh>
                    <SortableTh :ordering="ordering" field="last_login" @sort="sortBy">
                        Last login
                    </SortableTh>
                    <SortableTh :ordering="ordering" field="num_surfaces" numeric
                                @sort="sortBy">
                        Digital surface twins
                    </SortableTh>
                    <SortableTh :ordering="ordering" field="num_topographies" numeric
                                @sort="sortBy">
                        Measurements
                    </SortableTh>
                    <th scope="col"></th>
                </tr>
                </thead>
                <tbody>
                <tr v-for="user in items" :key="user.id">
                    <td>
                        <span class="fw-semibold">{{ user.name || "—" }}</span>
                        <i v-if="user.is_staff"
                           class="fa fa-user-shield ms-1 text-muted"
                           title="Staff user"></i>
                        <i v-if="!user.is_active"
                           class="fa fa-ban ms-1 text-danger"
                           title="Inactive account"></i>
                        <div class="small text-muted">{{ user.email }}</div>
                    </td>
                    <td class="font-monospace small">{{ user.username }}</td>
                    <td>
                        <a v-if="user.orcid" :href="`https://orcid.org/${user.orcid}`"
                           class="font-monospace small" rel="noopener"
                           target="_blank">{{ user.orcid }}</a>
                        <span v-else class="text-muted">–</span>
                    </td>
                    <td>
                        <TermsBadge :accepted-on="user.terms_accepted_on"
                                    :status="user.terms_status"></TermsBadge>
                    </td>
                    <td class="small">{{ formatTimestamp(user.date_joined) }}</td>
                    <td class="small">
                        <span v-if="user.last_login == null" class="text-muted">
                            Never
                        </span>
                        <span v-else>{{ formatTimestamp(user.last_login) }}</span>
                    </td>
                    <td class="text-end">{{ user.num_surfaces }}</td>
                    <td class="text-end">{{ user.num_topographies }}</td>
                    <td class="text-end">
                        <a v-if="user.admin_url" :href="user.admin_url"
                           class="text-muted" title="Open in Django admin">
                            <i class="fa fa-arrow-up-right-from-square"></i>
                        </a>
                    </td>
                </tr>
                <tr v-if="!isLoading && items.length === 0">
                    <td class="text-center text-muted py-4" colspan="9">
                        No users match this search.
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
