<script setup>
import {version, ref} from 'vue';

const _modal = ref(false);
const _versions = ref([]);
</script>

<template>
    <!-- Version Modal-->
    <b-modal v-model="_modal" title="Version information" size="lg" id="version-modal">
        <p>
            This cloud platform builds upon the open source software packages summarized in the following list.
        </p>
        <table class="table table-striped">
            <thead>
            <tr>
                <th>Module</th>
                <th>Version</th>
                {# Maybe also add links? #}
                <th>License</th>
                <th>Links</th>
            </tr>
            </thead>
            <tbody>
            <tr>
                <td>Vue.js</td>
                <td>{{ version }}</td>
                <td><a href="https://github.com/vuejs/vue/blob/main/LICENSE">
                    MIT
                </a></td>
                <td><a href="https://vuejs.org/">Website</a></td>
            </tr>
            <tr>
                <td>Bootstrap-5</td>
                <td></td>
                <td>MIT</td>
                <td><a href="https://getbootstrap.com/">Website</a></td>
            </tr>
            <tr>
                <td>bootstrap-vue-next</td>
                <td></td>
                <td><a href="https://github.com/bootstrap-vue-next/bootstrap-vue-next/blob/main/LICENSE">
                    MIT
                </a></td>
                <td><a href="https://github.com/bootstrap-vue-next/">Website</a></td>
            </tr>
            <tr>
                <td>OpenSeadragon</td>
                <td></td>
                <td><a href="https://github.com/ContactEngineering/topobank/blob/develop/LICENSE-openseadragon.txt">
                    BSD 3-Clause
                </a></td>
                <td><a href="https://openseadragon.github.io/">Website</a></td>
            </tr>
            <tr v-for="[key, value] in Object.entries(_versions)">
                <td>{{ key }}</td>
                <td>{{ value.version }}</td>
                <td>
                    {{ value.license }}
                </td>
                <td>
                    <a :href="value.homepage">Website</a>
                </td>
            </tr>
            </tbody>
        </table>
    </b-modal>
</template>