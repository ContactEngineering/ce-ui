<script setup lang="ts">
// Quasar notifications are handled via the Notify plugin - no orchestrator needed

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
    <header class="app-header">
        <Topnav />
        <Breadcrumbs :tabs="breadcrumbs" />
    </header>

    <main v-if="vueComponent != null && vueComponent.length > 0" class="app-main">
        <div class="app-content">
            <component :is="vueComponent" />
        </div>
    </main>
</template>

<style scoped>
.app-header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;
}

.app-main {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.app-content {
    max-width: 1400px;
    width: 100%;
    margin: 0 auto;
    padding: 24px;
}
</style>