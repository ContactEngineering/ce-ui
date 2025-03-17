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
        <a :href="versions.topobank.homepage">
            topobank
        </a> v{{ versions.topobank.version }},
        <a :href="versions.ce_ui.homepage">
            ui
        </a> v{{ versions.ce_ui.version }};
        <b>Plugins: </b>
        <a :href="versions.topobank_statistics.homepage">
            statistics
        </a> v{{ versions.topobank_statistics.version }},
        <a :href="versions.topobank_contact.homepage">
            contact mechanics
        </a> v{{ versions.topobank_contact.version }},
        <a :href="versions.topobank_publication.homepage">
            DOI
        </a> v{{ versions.topobank_publication.version }};
        <b>Backend: </b>
        <a :href="versions.SurfaceTopography.homepage">
            SurfaceTopography
        </a> v{{ versions.SurfaceTopography.version }}
    </div>
</template>