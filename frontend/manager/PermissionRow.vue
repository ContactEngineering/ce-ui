<script setup lang="ts">

import {onMounted, ref} from "vue";
import {BForm, BFormSelect, BPlaceholder, useToastController} from "bootstrap-vue-next";

import {usersV1UserRetrieve} from "@/api";
import {getIdFromUrl} from "@/utils/api";

const {show} = useToastController();

const userPermission = defineModel('userPermission', {required: true});

const props = defineProps({
    disabled: Boolean
});

const user = ref(null);

const options = [
    {value: 'no-access', text: 'Revoke access (unshare digital surface twin)'},
    {value: 'view', text: 'Allowed to view this digital surface twin'},
    {value: 'edit', text: 'Can edit (add, remove, modify measurements)'},
    {value: 'full', text: 'Full access (including publishing and access control)'}
];

onMounted(async () => {
    if (userPermission.value.user != null) {
        try {
            const userId = getIdFromUrl(userPermission.value.user);
            const response = await usersV1UserRetrieve({path: {id: userId}});
            user.value = response.data;
        } catch (error: any) {
            show?.({
                props: {
                    title: "Error while loading user",
                    body: error.message,
                    variant: "danger"
                }
            });
        }
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
