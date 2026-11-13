<script setup lang="ts">

import axios from "axios";
import {onMounted, ref} from "vue";
import {BForm, BFormSelect, BPlaceholder} from "bootstrap-vue-next";
import {needsUserDetails} from "@/utils/permissions";

const userPermission = defineModel('userPermission', {required: true});

const props = defineProps({
    disabled: Boolean
});

// Show what the row already knows about the user right away
const user = ref(userPermission.value.userData ?? null);

const options = [
    {value: 'no-access', text: 'Revoke access (unshare digital surface twin)'},
    {value: 'view', text: 'Allowed to view this digital surface twin'},
    {value: 'edit', text: 'Can edit (add, remove, modify measurements)'},
    {value: 'full', text: 'Full access (including publishing and access control)'}
];

onMounted(() => {
    // The ORCID iD is not part of the permission list, so fetch the user for it.
    // Failing to do so is not worth an error: the name is already shown, and
    // the user may not be visible to us (e.g. just found by exact name).
    if (userPermission.value.user != null && needsUserDetails(userPermission.value)) {
        axios.get(userPermission.value.user).then(response => {
            user.value = response.data;
        }).catch(() => {
            user.value ??= {url: userPermission.value.user, name: "Unknown user"};
        });
    }
});

</script>

<template>
    <BPlaceholder v-if="user == null" animation="glow"></BPlaceholder>
    <div v-if="user != null" class="row mb-2">
        <div class="col-4 my-auto">
            <b>{{ user.name }}</b>
            <br>
            {{ user.orcid }}
        </div>
        <div class="col-8">
            <BForm>
                <BFormSelect v-model="userPermission.permission"
                             :options="options"
                             :disabled="disabled">
                </BFormSelect>
            </BForm>
        </div>
    </div>
</template>
