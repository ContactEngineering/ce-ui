<script setup lang="ts">

import axios from "axios";
import {computed, onMounted, ref} from "vue";

import {
    BAlert,
    BButton,
    BButtonGroup,
    BSpinner,
    useToast
} from 'bootstrap-vue-next';

import SearchUserModal from "@/components/ui/SearchUserModal.vue";
import PermissionRow from "@/components/manager/PermissionRow.vue";
import Toolbar from "@/components/ui/Toolbar.vue";
import LoadingIndicator from '@/components/ui/LoadingIndicator.vue';

const toast = useToast();

const props = defineProps({
    // v2 permission-set endpoint of the dataset
    permissionsUrl: String
});

const isEditing = ref(false);
const isSaving = ref(false);
const searchUser = ref(false);

/* Rows in the shape PermissionRow works on: {user: <url>, permission: <level>}.
   The current user's row is read-only; the others can be edited with full
   access. */
const _api = ref(null);  // grant/revoke routes reported by the permission set
const currentUser = ref(null);
const otherUsers = ref([]);
const savedOtherUsers = ref([]);

onMounted(loadPermissions);

function loadPermissions() {
    axios.get(props.permissionsUrl).then(response => {
        _api.value = response.data.api;
        const rows = response.data.user_permissions.map(p => {
            return {user: p.user.url, permission: p.allow, isCurrentUser: p.is_current_user};
        });
        currentUser.value = rows.find(row => row.isCurrentUser) ?? null;
        otherUsers.value = rows.filter(row => !row.isCurrentUser);
    }).catch(error => {
        toast.create({
            title: "Failed to fetch permissions",
            body: error,
            variant: 'danger'
        })?.show();
    });
}

const hasFullAccess = computed(() => {
    return currentUser.value?.permission === 'full';
});

function saveCard() {
    isEditing.value = false;
    isSaving.value = true;
    // Grant changed access levels; a row set to 'no-access' is a revocation
    const saved = new Map(savedOtherUsers.value.map(row => [row.user, row.permission]));
    const requests = [];
    for (const row of otherUsers.value) {
        if (saved.get(row.user) === row.permission) {
            continue;  // unchanged
        }
        if (row.permission === 'no-access') {
            requests.push(axios.post(_api.value.revoke_user_access, {user: row.user}));
        } else {
            requests.push(axios.post(_api.value.grant_user_access, {user: row.user, allow: row.permission}));
        }
    }
    Promise.all(requests).catch(error => {
        toast.create({
            title: "Permission update failed",
            body: error,
            variant: 'danger'
        })?.show();
    }).finally(() => {
        // Re-read the authoritative state, whether saving succeeded or not
        loadPermissions();
        isSaving.value = false;
    });
}

function addUser(user) {
    searchUser.value = false;
    otherUsers.value.push({user: user.url, permission: 'view'});
}

</script>

<template>
    <LoadingIndicator v-if="currentUser == null"/>
    <div v-if="currentUser != null">
        <Toolbar v-if="hasFullAccess">
            <BButtonGroup v-if="isEditing || isSaving"
                          class="me-2"
                          size="sm">
                <BButton v-if="isEditing"
                         variant="primary"
                         @click="searchUser = !searchUser">
                    Add user (share dataset)
                </BButton>
            </BButtonGroup>
            <BButtonGroup
                v-if="!isEditing && !isSaving"
                size="sm">
                <BButton variant="primary"
                         @click="savedOtherUsers = JSON.parse(JSON.stringify(otherUsers)); isEditing = true">
                    <i class="fa fa-pen me-1"></i>Edit
                </BButton>
            </BButtonGroup>
            <BButtonGroup v-if="isEditing || isSaving"
                          size="sm">
                <BButton v-if="isEditing"
                         variant="danger"
                         @click="isEditing = false; otherUsers = savedOtherUsers">
                    Discard
                </BButton>
                <BButton variant="success"
                         @click="saveCard">
                    <BSpinner small v-if="isSaving"></BSpinner>
                    Save
                </BButton>
            </BButtonGroup>
        </Toolbar>
        <BAlert v-if="isEditing" :model-value="true" variant="secondary">
            <i class="fa-solid fa-circle-info me-2"></i>Access levels:
            <b>View</b> can see the data; <b>Edit</b> can also add, remove and
            modify measurements; <b>Full</b> can additionally publish and manage
            who has access.
        </BAlert>
        <PermissionRow :user-permission="currentUser"
                       :disabled="true">
        </PermissionRow>
        <hr/>
        <div v-if="otherUsers.length === 0">
            Only you can access this digital surface twin.
        </div>
        <PermissionRow v-if="otherUsers.length > 0"
                       v-for="(userPermission, index) in otherUsers"
                       v-model:user-permission="otherUsers[index]"
                       :disabled="!isEditing">
        </PermissionRow>
    </div>
    <SearchUserModal v-model="searchUser"
                     @user-selected="addUser">
    </SearchUserModal>
</template>
