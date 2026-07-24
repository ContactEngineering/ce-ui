<script setup lang="ts">

import axios from "axios";
import {ref} from "vue";

import {
    BAlert,
    BButton,
    BButtonGroup,
    BSpinner,
    useToastController
} from 'bootstrap-vue-next';

import SearchUserModal from "@/components/ui/SearchUserModal.vue";
import PermissionRow from "@/components/manager/PermissionRow.vue";

const {show} = useToastController();

const props = defineProps({
    setPermissionsUrl: String,
    permissions: Object
});

const emit = defineEmits([
    'update:permissions'
]);

const isEditing = ref(false);
const isSaving = ref(false);
const selfPermissions = ref(props.permissions);
const savedPermissions = ref(props.permissions);
const searchUser = ref(false);

function saveCard() {
    isEditing.value = false;
    isSaving.value = true;
    axios.patch(props.setPermissionsUrl, selfPermissions.value.other_users).then(response => {
        emit('update:permissions', response.data);
    }).catch(error => {
        show?.({
            props: {
                title: "Permission update failed",
                body: error,
                variant: 'danger'
            }
        });
        selfPermissions.value = savedPermissions.value;
    }).finally(() => {
        isSaving.value = false;
    });
}

function addUser(user) {
    searchUser.value = false;
    selfPermissions.value.other_users.push({user: user.url, permission: 'view'});
}

</script>

<template>
    <div>
        <div v-if="selfPermissions.current_user.permission === 'full'"
             class="d-flex justify-content-end align-items-center border-bottom pb-2 mb-3">
            <BButtonGroup v-if="isEditing || isSaving"
                          class="me-2"
                          size="sm">
                <BButton v-if="isEditing"
                         variant="outline-secondary"
                         @click="searchUser = !searchUser">
                    Add user (share dataset)
                </BButton>
            </BButtonGroup>
            <BButtonGroup
                v-if="!isEditing && !isSaving"
                size="sm">
                <BButton variant="outline-secondary"
                         @click="savedPermissions = JSON.parse(JSON.stringify(selfPermissions)); isEditing = true">
                    <i class="fa fa-pen me-1"></i>Edit
                </BButton>
            </BButtonGroup>
            <BButtonGroup v-if="isEditing || isSaving"
                          size="sm">
                <BButton v-if="isEditing"
                         variant="danger"
                         @click="isEditing = false; selfPermissions = savedPermissions">
                    Discard
                </BButton>
                <BButton variant="success"
                         @click="saveCard">
                    <BSpinner small v-if="isSaving"></BSpinner>
                    Save
                </BButton>
            </BButtonGroup>
        </div>
        <BAlert v-if="isEditing" :model-value="true" variant="secondary">
            <i class="fa-solid fa-circle-info me-2"></i>Access levels:
            <b>View</b> can see the data; <b>Edit</b> can also add, remove and
            modify measurements; <b>Full</b> can additionally publish and manage
            who has access.
        </BAlert>
        <PermissionRow :user-permission="selfPermissions.current_user"
                       :disabled="true">
        </PermissionRow>
        <hr/>
        <div v-if="selfPermissions.other_users.length === 0">
            Only you can access this digital surface twin.
        </div>
        <PermissionRow v-if="selfPermissions.other_users.length > 0"
                       v-for="(userPermission, index) in selfPermissions.other_users"
                       v-model:user-permission="selfPermissions.other_users[index]"
                       :disabled="!isEditing">
        </PermissionRow>
    </div>
    <SearchUserModal v-model="searchUser"
                     @user-selected="addUser">
    </SearchUserModal>
</template>
