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
const selfPermissions = ref(props.permissions);
const savedPermissions = ref(props.permissions);
const searchUser = ref(false);

function saveCard() {
    isEditing.value = false;
    isSaving.value = true;
    axios.patch(`${props.surfaceUrl}set-permissions/`, selfPermissions.value.other_users).then(response => {
        emit('update:permissions', response.data);
    }).catch(error => {
        show?.({
            props: {
                title: "Permission update failed",
                body: error,
                variant: 'danger'
            }
        });
        selfPermissions.value = this.savedPermissions;
    }).finally(() => {
        isSaving.value = false;
    });
}

function addUser(user) {
    searchUser.value = false;
    selfPermissions.value.other_users.push({user: user, permission: 'view'});
}

</script>

<template>
    <BCard>
        <template #header>
            <h5 class="float-start">Permissions</h5>
            <BButtonGroup
                v-if="!isEditing && !isSaving && selfPermissions.current_user.permission === 'full'"
                class="float-end"
                size="sm">
                <BButton variant="outline-secondary"
                         @click="savedPermissions = JSON.parse(JSON.stringify(selfPermissions)); isEditing = true">
                    <i class="fa fa-pen"></i>
                </BButton>
            </BButtonGroup>
            <BButtonGroup v-if="isEditing || isSaving"
                          class="float-end"
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
        </BCardBody>
    </BCard>
    <SearchUserModal v-model="searchUser"
                     @user-selected="addUser">
    </SearchUserModal>
</template>
