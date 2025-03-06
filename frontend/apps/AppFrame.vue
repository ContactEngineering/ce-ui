<script setup>

import Breadcrumbs from "../base/Breadcrumbs.vue";
import Topnav from "../base/Topnav.vue";

const props = defineProps({
    vueComponent: String,
    // Breadcrumb navigation
    breadcrumbs: Object,
    // Django messages
    messages: Array
})

</script>

<template>
    <div class="fixed-top">
        <Topnav></Topnav>
        <Breadcrumbs :tabs="breadcrumbs"></Breadcrumbs>
    </div>

    <div id="wrapper">
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