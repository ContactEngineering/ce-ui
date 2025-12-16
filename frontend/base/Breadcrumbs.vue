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
    <nav class="breadcrumb-bar">
        <div class="breadcrumb-content">
            <template v-for="(tab, index) in tabs" :key="index">
                <div class="breadcrumb-item" :title="tab.tooltip">
                    <a v-if="tab.href_previous != null"
                       class="nav-arrow"
                       :href="tab.href_previous"
                       aria-label="Previous">
                        <i class="fa fa-chevron-left"></i>
                    </a>
                    <a class="breadcrumb-link"
                       :class="{ 'active': tab.active }"
                       :href="tab.href">
                        <i :class="iconClass(tab)"></i>
                        <span>{{ tab.title }}</span>
                    </a>
                    <a v-if="tab.href_next != null"
                       class="nav-arrow"
                       :href="tab.href_next"
                       aria-label="Next">
                        <i class="fa fa-chevron-right"></i>
                    </a>
                </div>
                <i v-if="index !== 0 && index !== tabs.length - 1"
                   class="fa fa-chevron-right separator"></i>
            </template>
        </div>
    </nav>
</template>

<style scoped>
.breadcrumb-bar {
    background-color: var(--md-sys-color-surface-container-low);
    padding: 12px 24px;
}

.breadcrumb-content {
    display: flex;
    align-items: center;
    gap: 8px;
    max-width: 1400px;
    margin: 0 auto;
}

.breadcrumb-item {
    display: flex;
    align-items: center;
    gap: 4px;
}

.breadcrumb-link {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    border-radius: var(--md-sys-shape-corner-small);
    color: var(--md-sys-color-on-surface-variant);
    text-decoration: none;
    font-size: var(--md-sys-typescale-label-large-size);
    font-weight: 500;
    transition: all 0.2s ease;
}

.breadcrumb-link:hover {
    background-color: var(--md-sys-color-surface-container-high);
    color: var(--md-sys-color-on-surface);
}

.breadcrumb-link.active {
    background-color: var(--md-sys-color-primary-container);
    color: var(--md-sys-color-on-primary-container);
}

.nav-arrow {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: var(--md-sys-shape-corner-full);
    color: var(--md-sys-color-on-surface-variant);
    text-decoration: none;
    transition: all 0.2s ease;
}

.nav-arrow:hover {
    background-color: var(--md-sys-color-surface-container-high);
    color: var(--md-sys-color-on-surface);
}

.separator {
    color: var(--md-sys-color-outline);
    font-size: 10px;
}
</style>