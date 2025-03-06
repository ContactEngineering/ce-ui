<script setup>

import Breadcrumbs from "./Breadcrumbs.vue";
import Topnav from "./Topnav.vue";

const props = defineProps({
    vueComponent: String,
    // Breadcrumb navigation
    breadcrumbs: Object,
    // Admin and login URLs
    adminUrl: String,
    loginUrl: String,
    // User information
    userApiUrl: String,
    userName: String,
    userFullName: String,
    userOrcid: String,
    userIsAnonymous: Boolean,
    userIsStaff: Boolean,
    // Django messages
    messages: Array
})

</script>

<template>
    <div class="fixed-top">
        <Topnav></Topnav>
        <Breadcrumbs></Breadcrumbs>
    </div>

    <div id="wrapper">
        <div id="content-wrapper">
            <div class="container-fluid mt-1">
                <div class="tab-content mt-2">
                    <div class="tab-pane active">
                        <div id="search-results">
                            Div here
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>