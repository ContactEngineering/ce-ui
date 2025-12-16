<script setup lang="ts">
import { QLayout, QHeader, QPageContainer, QPage, QFooter, QToolbar, QSpace } from "quasar";

import Breadcrumbs from "../base/Breadcrumbs.vue";
import Topnav from "../base/Topnav.vue";

const props = defineProps({
    vueComponent: { type: String, default: null },
    breadcrumbs: Object,
    messages: Array
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

        <QPageContainer>
            <QPage padding>
                <component v-if="vueComponent != null && vueComponent.length > 0" :is="vueComponent" />
            </QPage>
        </QPageContainer>

        <QFooter elevated class="bg-white text-dark q-pa-sm">
            <QToolbar>
                <QSpace />
                <div class="row items-center q-gutter-md">
                    <a href="https://pastewka.org/" target="_blank">
                        <img src="/static/images/uni_freiburg_logo.png" height="48px" alt="University of Freiburg">
                    </a>
                    <a href="http://www.engineering.pitt.edu/TevisJacobs/" target="_blank">
                        <img src="/static/images/pitt_logo.png" height="48px" alt="University of Pittsburgh">
                    </a>
                    <span class="text-caption">Funding by</span>
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
                <QSpace />
            </QToolbar>
        </QFooter>
    </QLayout>
</template>
