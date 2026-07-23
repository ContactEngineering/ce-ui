<script setup lang="ts">

import axios from "axios";
import {onMounted, ref} from "vue";

const props = defineProps({
    apiUrl: {
        type: String,
        default: '/manager/api/versions/'
    }
});

const versions = ref(null);

onMounted(() => {
    axios.get(props.apiUrl)
        .then(response => {
            versions.value = response.data;
        });
});

</script>

<template>
    <div v-if="versions" class="pe-3 small">
        <b>Core: </b>
        <a v-if="versions.topobank" :href="versions.topobank.homepage">
            topobank
        </a><span v-if="versions.topobank"> v{{ versions.topobank.version }},</span>
        <a v-if="versions.ce_ui" :href="versions.ce_ui.homepage">
            ui
        </a><span v-if="versions.ce_ui"> v{{ versions.ce_ui.version }}</span>;
        <b>Plugins: </b>
        <a v-if="versions.topobank_statistics" :href="versions.topobank_statistics.homepage">
            statistics
        </a><span v-if="versions.topobank_statistics"> v{{ versions.topobank_statistics.version }},</span>
        <a v-if="versions.topobank_contact" :href="versions.topobank_contact.homepage">
            contact mechanics
        </a><span v-if="versions.topobank_contact"> v{{ versions.topobank_contact.version }},</span>
        <a v-if="versions.topobank_publication" :href="versions.topobank_publication.homepage">
            DOI
        </a><span v-if="versions.topobank_publication"> v{{ versions.topobank_publication.version }}</span>;
        <b>Backend: </b>
        <a v-if="versions.SurfaceTopography" :href="versions.SurfaceTopography.homepage">
            SurfaceTopography
        </a><span v-if="versions.SurfaceTopography"> v{{ versions.SurfaceTopography.version }}</span>
    </div>
</template>