<script setup>

import {
    QDialog,
    QCard,
    QCardSection,
    QCardActions,
    QBtn
} from "quasar";

const visible = defineModel('visible', { required: true });

const props = defineProps({
    dois: {
        type: Object,
        default: []
    },
});

</script>

<template>
    <QDialog v-model="visible">
        <QCard style="min-width: 600px; max-width: 900px">
            <QCardSection>
                <div class="text-h6">Bibliography</div>
            </QCardSection>
            <QCardSection>
                <div v-if="dois.length > 0">
                    This analysis used methods and algorithms described in the following publications:
                    <ul>
                        <li v-for="doi in dois" :key="doi">
                            <a :href="`https://doi.org/${doi}`" target="_blank">{{ doi }}</a>
                        </li>
                    </ul>
                </div>
                <div v-if="dois.length == 0">
                    No bibliography related to these analyses was reported.
                </div>
            </QCardSection>
            <QCardActions align="right">
                <QBtn flat label="Close" v-close-popup />
            </QCardActions>
        </QCard>
    </QDialog>
</template>
