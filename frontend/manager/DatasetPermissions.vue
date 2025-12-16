<script setup lang="ts">

import {ref} from "vue";

import {
    QBtn,
    QBtnGroup,
    QCard,
    QCardSection,
    QSpinner
} from 'quasar';

import { useNotify } from "@/utils/notify";
import {managerApiSurfaceSetPermissionsPartialUpdate} from "@/api";
import {getIdFromUrl} from "@/utils/api";

import SearchUserModal from "../components/SearchUserModal.vue";
import PermissionRow from "topobank/manager/PermissionRow.vue";

const { show } = useNotify();

const props = defineProps({
    setPermissionsUrl: String,
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

async function saveCard() {
    isEditing.value = false;
    isSaving.value = true;
    try {
        const surfaceId = getIdFromUrl(props.setPermissionsUrl);
        const response = await managerApiSurfaceSetPermissionsPartialUpdate({
            path: {id: surfaceId},
            body: selfPermissions.value.other_users
        });
        emit('update:permissions', response.data);
    } catch (error) {
        show?.({
            props: {
                title: "Permission update failed",
                body: error,
                variant: 'danger'
            }
        });
        selfPermissions.value = savedPermissions.value;
    } finally {
        isSaving.value = false;
    }
}

function addUser(user) {
    searchUser.value = false;
    selfPermissions.value.other_users.push({user: user.url, permission: 'view'});
}

</script>

<template>
    <QCard>
        <QCardSection class="flex items-center">
            <h5 class="q-ma-none col-grow">Permissions</h5>
            <QBtnGroup
                v-if="!isEditing && !isSaving && selfPermissions.current_user.permission === 'full'"
                flat>
                <QBtn flat size="sm" icon="edit"
                      @click="savedPermissions = JSON.parse(JSON.stringify(selfPermissions)); isEditing = true" />
            </QBtnGroup>
            <QBtnGroup v-if="isEditing || isSaving" flat class="q-mr-sm">
                <QBtn v-if="isEditing"
                      flat size="sm"
                      @click="searchUser = !searchUser">
                    Add user (share dataset)
                </QBtn>
            </QBtnGroup>
            <QBtnGroup v-if="isEditing || isSaving" flat>
                <QBtn v-if="isEditing"
                      color="negative" size="sm"
                      @click="isEditing = false; selfPermissions = savedPermissions">
                    Discard
                </QBtn>
                <QBtn color="positive" size="sm"
                      @click="saveCard">
                    <QSpinner v-if="isSaving" size="1rem" class="q-mr-sm" />
                    Save
                </QBtn>
            </QBtnGroup>
        </QCardSection>
        <QCardSection>
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
        </QCardSection>
    </QCard>
    <SearchUserModal v-model="searchUser"
                     @user-selected="addUser">
    </SearchUserModal>
</template>
