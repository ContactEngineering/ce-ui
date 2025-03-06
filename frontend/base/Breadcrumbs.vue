<script setup>

const props = defineProps({
    tabs: {
        type: Array,
        default: []
    }
});

function iconClass(tab) {
    const c = {};
    c['fa'] = true;
    c[`fa-${tab.icon}`] = true;
    return c;
}

</script>

<template>
    <ul role="tablist"
        class="nav nav-tabs lined-tabs align-items-center bg-light w-100 shadow">
        <li v-for="(tab, index) in tabs"
            class="nav-item d-flex"
            :title="tab.tooltip">
            <div :class="{ 'nav-link': true, 'active': tab.active }">
                <a v-if="tab.href_previous != null"
                   class="link-underline link-underline-opacity-0"
                   :href="tab.href_previous">
                    <i class="fa fa-caret-left"></i>
                </a>
                <a class="link-offset-2 link-underline link-underline-opacity-0 link-underline-opacity-75-hover"
                   :href="tab.href">
                    <i :class="iconClass(tab)"></i>
                    {{ tab.title }}
                </a>
                <a v-if="tab.href_next != null"
                   class="link-underline link-underline-opacity-0"
                   :href="tab.href_next">
                    <i class="fa fa-caret-right"></i>
                </a>
            </div>
            <div v-if="index !== 0 && index !== tabs.length - 1" class="nav-pad-y">
                /
            </div>
        </li>
    </ul>
</template>

<style scoped>
.nav-pad-y {
    padding: var(--bs-nav-link-padding-y) 0;
}
</style>