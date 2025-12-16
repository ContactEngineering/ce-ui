<script setup>
import { version, ref } from 'vue';
import {
    QDialog,
    QCard,
    QCardSection,
    QCardActions,
    QBtn,
    QMarkupTable
} from "quasar";

const _modal = ref(false);
const _versions = ref([]);
</script>

<template>
    <!-- Version Modal-->
    <QDialog v-model="_modal">
        <QCard style="min-width: 600px; max-width: 800px">
            <QCardSection>
                <div class="text-h6">Version information</div>
            </QCardSection>
            <QCardSection>
                <p>
                    This cloud platform builds upon the open source software packages summarized in the following list.
                </p>
                <QMarkupTable>
                    <thead>
                    <tr>
                        <th class="text-left">Module</th>
                        <th class="text-left">Version</th>
                        <th class="text-left">License</th>
                        <th class="text-left">Links</th>
                    </tr>
                    </thead>
                    <tbody>
                    <tr>
                        <td>Vue.js</td>
                        <td>{{ version }}</td>
                        <td><a href="https://github.com/vuejs/vue/blob/main/LICENSE">MIT</a></td>
                        <td><a href="https://vuejs.org/">Website</a></td>
                    </tr>
                    <tr>
                        <td>Quasar</td>
                        <td></td>
                        <td><a href="https://github.com/quasarframework/quasar/blob/dev/LICENSE">MIT</a></td>
                        <td><a href="https://quasar.dev/">Website</a></td>
                    </tr>
                    <tr>
                        <td>OpenSeadragon</td>
                        <td></td>
                        <td><a href="https://github.com/ContactEngineering/topobank/blob/develop/LICENSE-openseadragon.txt">BSD 3-Clause</a></td>
                        <td><a href="https://openseadragon.github.io/">Website</a></td>
                    </tr>
                    <tr v-for="[key, value] in Object.entries(_versions)" :key="key">
                        <td>{{ key }}</td>
                        <td>{{ value.version }}</td>
                        <td>{{ value.license }}</td>
                        <td><a :href="value.homepage">Website</a></td>
                    </tr>
                    </tbody>
                </QMarkupTable>
            </QCardSection>
            <QCardActions align="right">
                <QBtn flat label="Close" v-close-popup />
            </QCardActions>
        </QCard>
    </QDialog>
</template>