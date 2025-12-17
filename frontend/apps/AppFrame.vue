<script setup lang="ts">
import { provide, ref } from "vue";
import { QLayout, QHeader, QPageContainer, QPage, QToolbar, QSpace, QDrawer, QSeparator } from "quasar";

import Breadcrumbs from "../base/Breadcrumbs.vue";
import Topnav from "../base/Topnav.vue";
import NotificationDrawer from "../base/NotificationDrawer.vue";
import UserMenuDrawer from "../base/UserMenuDrawer.vue";

const props = defineProps({
    vueComponent: { type: String, default: null },
    breadcrumbs: Object,
    messages: Array
});

// Right drawer state
const rightDrawerOpen = ref(false);
const rightDrawerContent = ref<'notifications' | 'user' | null>(null);

function openDrawer(content: 'notifications' | 'user') {
    rightDrawerContent.value = content;
    rightDrawerOpen.value = true;
}

function closeDrawer() {
    rightDrawerOpen.value = false;
}

// Provide drawer controls to child components
provide('rightDrawer', {
    open: openDrawer,
    close: closeDrawer,
    isOpen: rightDrawerOpen,
    content: rightDrawerContent
});

</script>

<template>
    <QLayout view="hHh lpR fFf">
        <QHeader elevated>
            <Topnav :messages="messages" />
            <QToolbar v-if="breadcrumbs && breadcrumbs.length > 0">
                <Breadcrumbs :tabs="breadcrumbs" />
            </QToolbar>
        </QHeader>

        <QDrawer v-model="rightDrawerOpen" side="right" overlay bordered :width="320">
            <NotificationDrawer v-if="rightDrawerContent === 'notifications'" />
            <UserMenuDrawer v-if="rightDrawerContent === 'user'" />
        </QDrawer>

        <QPageContainer>
            <QPage padding class="column">
                <div class="col">
                    <component v-if="vueComponent != null && vueComponent.length > 0" :is="vueComponent" />
                </div>

                <!-- Footer - scrolls with content -->
                <footer class="page-footer q-mt-xl q-pt-md">
                    <QSeparator class="q-mb-md" />
                    <div class="row items-center justify-center q-gutter-md">
                        <a href="https://pastewka.org/" target="_blank">
                            <img src="/static/images/uni_freiburg_logo.png" height="48px" alt="University of Freiburg">
                        </a>
                        <a href="http://www.engineering.pitt.edu/TevisJacobs/" target="_blank">
                            <img src="/static/images/pitt_logo.png" height="48px" alt="University of Pittsburgh">
                        </a>
                        <span class="text-caption text-grey-7">Funding by</span>
                        <a href="https://erc.europa.eu/" target="_blank">
                            <img src="/static/images/erc_logo.png" height="48px" alt="ERC">
                        </a>
                        <a href="https://www.livmats.uni-freiburg.de/" target="_blank">
                            <img src="/static/images/logo_livmats_small.jpg" height="48px" alt="livMatS">
                        </a>
                        <a href="https://www.nsf.gov/" target="_blank">
                            <img src="/static/images/nsf_logo.png" height="48px" alt="NSF">
                        </a>
                    </div>
                </footer>
            </QPage>
        </QPageContainer>
    </QLayout>
</template>

<style scoped>
.page-footer {
    flex-shrink: 0;
}
</style>
