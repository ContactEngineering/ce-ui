<script setup lang="ts">

import {onMounted, ref} from "vue";
import { QSelect, QSkeleton } from "quasar";

import { useNotify } from "@/utils/notify";
import {usersV1UserRetrieve} from "@/api";
import {getIdFromUrl} from "@/utils/api";

const { show } = useNotify();

const userPermission = defineModel('userPermission', {required: true});

const props = defineProps({
    disabled: Boolean
});

const user = ref(null);

const options = [
    {value: 'no-access', label: 'Revoke access (unshare digital surface twin)'},
    {value: 'view', label: 'Allowed to view this digital surface twin'},
    {value: 'edit', label: 'Can edit (add, remove, modify measurements)'},
    {value: 'full', label: 'Full access (including publishing and access control)'}
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
    <QSkeleton v-if="user == null" type="rect" height="40px" />
    <div v-if="user != null" class="row q-mb-sm">
        <div class="col-4 self-center">
            <b>{{ user.name }}</b>
            <br>
            {{ user.orcid }}
        </div>
        <div class="col-8">
            <QSelect v-model="userPermission.permission"
                     :options="options"
                     :disable="disabled"
                     emit-value
                     map-options
                     dense
                     outlined />
        </div>
    </div>
</template>
