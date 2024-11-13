<script setup>

import axios from "axios";
import {ref} from "vue";

import {
    BButton,
    BButtonGroup,
    BCard,
    BCardBody,
    BSpinner,
    useToastController
} from 'bootstrap-vue-next';

import SearchUserModal from "../components/SearchUserModal.vue";
import PermissionRow from "topobank/manager/PermissionRow.vue";

const {show} = useToastController();

const props = defineProps({
    surfaceUrl: String,
    permissions: Object
});

const emit = defineEmits([
    'updated:permissions'
]);

const isEditing = ref(false);
const isSaving = ref(false);
const permissions = ref(props.permissions);
const savedPermissions = ref(props.permissions);
const searchUser = ref(false);

function saveCard() {
    isEditing.value = false;
    isSaving.value = true;
    axios.patch(`${props.surfaceUrl}set-permissions/`, permissions.value.other_users).then(response => {
        emit('update:permissions', response.data);
    }).catch(error => {
        show?.({
            props: {
                title: "Permission update failed",
                body: error,
                variant: 'danger'
            }
        });
        permissions.value = this.savedPermissions;
    }).finally(() => {
        isSaving.value = false;
    });
}

function addUser(user) {
    searchUser.value = false;
    permissions.value.other_users.push({user: user, permission: 'view'});
}

</script>

<template>
    <BCard>
        <template #header>
            <h5 class="float-start">Permissions</h5>
            <BButtonGroup
                v-if="!isEditing && !isSaving && permissions.current_user.permission === 'full'"
                class="float-end"
                size="sm">
                <BButton variant="outline-secondary"
                         @click="savedPermissions = JSON.parse(JSON.stringify(permissions)); isEditing = true">
                    <i class="fa fa-pen"></i>
                </BButton>
            </BButtonGroup>
            <BButtonGroup v-if="isEditing || isSaving"
                          class="float-end"
                          size="sm">
                <BButton v-if="isEditing"
                         variant="danger"
                         @click="isEditing = false; permissions = savedPermissions">
                    Discard
                </BButton>
                <BButton variant="success"
                         @click="saveCard">
                    <BSpinner small v-if="isSaving"></BSpinner>
                    Save
                </BButton>
            </BButtonGroup>
            <BButtonGroup v-if="isEditing || isSaving"
                          class="float-end me-2"
                          size="sm">
                <BButton v-if="isEditing"
                         variant="outline-secondary"
                         @click="searchUser = !searchUser">
                    Add user (share dataset)
                </BButton>
            </BButtonGroup>
        </template>
        <BCardBody>
            <PermissionRow :user-permission="permissions.current_user"
                           :disabled="true">
            </PermissionRow>
            <hr/>
            <div v-if="permissions.other_users.length === 0">
                Only you can access this digital surface twin.
            </div>
            <PermissionRow v-if="permissions.other_users.length > 0"
                           v-for="userPermission in permissions.other_users"
                           v-model:user-permission="userPermission"
                           :disabled="!isEditing">
            </PermissionRow>
        </BCardBody>
    </BCard>
    <SearchUserModal v-model="searchUser"
                     @user-selected="addUser">
    </SearchUserModal>
</template>
