<script setup lang="ts">

import { BToastOrchestrator } from "bootstrap-vue-next";

import Breadcrumbs from "../base/Breadcrumbs.vue";
import Topnav from "../base/Topnav.vue";

const props = defineProps({
    vueComponent: { type: String, default: null },
    // Breadcrumb navigation
    breadcrumbs: Object,
    // Django messages
    messages: Array
});

</script>

<template>
    <BToastOrchestrator></BToastOrchestrator>
    <div class="fixed-top">
        <Topnav></Topnav>
        <Breadcrumbs :tabs="breadcrumbs"></Breadcrumbs>
    </div>

    <div v-if="vueComponent != null && vueComponent.length > 0" id="wrapper">
        <div id="content-wrapper">
            <div class="container-fluid mt-1">
                <div class="tab-content mt-2">
                    <div class="tab-pane active">
                        <component :is="vueComponent">
                        </component>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>