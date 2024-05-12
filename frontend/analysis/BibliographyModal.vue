<script setup>

import {BModal} from "bootstrap-vue-next";

const visible = defineModel('visible', {required: true});

const props = defineProps({
    dois: {
        type: Object,
        default: []
    },
});

</script>

<template>
    <BModal v-model="visible"
            size="xl"
            title="Bibliography"
            :ok-only="true"
            ok-title="Close">
        <div v-if="dois.length > 0" class="modal-body">
            This analysis used methods and algorithms described in the following publications:
            <ul>
                <li v-for="doi in dois">
                    <a :href="`https://doi.org/${doi}`" target="_blank">{{ doi }}</a>
                </li>
            </ul>
        </div>
        <div v-if="dois.length == 0" class="modal-body">
            No bibliography related to these analyses was reported.
        </div>
    </BModal>
</template>
