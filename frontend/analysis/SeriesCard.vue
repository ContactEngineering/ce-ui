<script setup lang="ts">

import { computed, onMounted, ref } from "vue";

import { QItem, QItemSection, QSeparator } from "quasar";

import { useNotify } from "@/utils/notify";
import { analysisApiCardSeriesRetrieve } from "@/api";
import { subjectsToBase64 } from "@/utils/api";

import AnalysisCard from "./AnalysisCard.vue";
import BokehPlot from "../components/BokehPlot.vue";

const { show } = useNotify();

const props = defineProps({
    apiUrl: {
        type: String,
        default: "/analysis/api/card/series"
    },
    detailUrl: {
        type: String,
        default: "/ui/analysis-detail/"
    },
    enlarged: {
        type: Boolean,
        default: true
    },
    functionName: {
        type: String,
        required: true
    },
    subjects: {
        type: Object,
        required: true
    }
});

// Information about analyses that this card display
const _title = ref(props.functionName);
const _analyses = ref(null);

// Plot configuration
const _categories = ref(null);
const _dataSources = ref(null);
const _outputBackend = ref("svg");
const _plots = ref(null);
const _showSymbols = ref(true);

// GUI logic
const _nbPendingAjaxRequests = ref(0);

// Auxiliary information
const _dois = ref([]);
const _messages = ref([]);


onMounted(() => {
    updateCard();
});

const analysisIds = computed(() => {
    if (_analyses.value == null) {
        return [];
    } else {
        return _analyses.value.map(a => a.id).join();
    }
});

async function updateCard() {
    /* Fetch JSON describing the card */
    _nbPendingAjaxRequests.value++;
    try {
        const response = await analysisApiCardSeriesRetrieve({
            path: {workflow: props.functionName},
            query: {subjects: subjectsToBase64(props.subjects)}
        } as any);
        _analyses.value = response.data.analyses;
        _title.value = response.data.plotConfiguration.title;
        _plots.value = [{
            title: "default",
            xAxisLabel: response.data.plotConfiguration.xAxisLabel,
            yAxisLabel: response.data.plotConfiguration.yAxisLabel,
            xAxisType: response.data.plotConfiguration.xAxisType,
            yAxisType: response.data.plotConfiguration.yAxisType
        }];
        _dataSources.value = response.data.plotConfiguration.dataSources;
        _categories.value = response.data.plotConfiguration.categories;
        _outputBackend.value = response.data.plotConfiguration.outputBackend;
        _showSymbols.value = response.data.plotConfiguration.showSymbols;
        _dois.value = response.data.dois;
        _messages.value = response.data.messages;
    } catch (error: any) {
        show?.({
            props: {
                title: "Error fetching analysis result",
                body: error.message,
                variant: "danger"
            }
        });
    } finally {
        _nbPendingAjaxRequests.value--;
    }
}

</script>

<template>
    <AnalysisCard v-model:analyses="_analyses"
                  :detailUrl="detailUrl"
                  :dois="_dois"
                  :enlarged="enlarged"
                  :functionName="functionName"
                  :messages="_messages"
                  :showLoadingSpinner="_nbPendingAjaxRequests > 0"
                  :subjects="subjects"
                  :title="_title"
                  @allTasksFinished="updateCard"
                  @refreshButtonClicked="updateCard"
                  @someTasksFinished="updateCard">
        <template #dropdowns>
            <QSeparator />
            <QItem clickable v-close-popup :href="`/analysis/download/${analysisIds}/txt`">
                <QItemSection>Download TXT</QItemSection>
            </QItem>
            <QItem clickable v-close-popup :href="`/analysis/download/${analysisIds}/csv`">
                <QItemSection>Download CSV</QItemSection>
            </QItem>
            <QItem clickable v-close-popup :href="`/analysis/download/${analysisIds}/xlsx`">
                <QItemSection>Download XLSX</QItemSection>
            </QItem>
            <QItem clickable v-close-popup @click="$refs.plot.download()">
                <QItemSection>Download SVG</QItemSection>
            </QItem>
        </template>
        <BokehPlot v-model:nbPendingAjaxRequests="_nbPendingAjaxRequests"
                   :categories="_categories"
                   :dataSources="_dataSources"
                   :functionTitle="_title"
                   :outputBackend="_outputBackend"
                   :plots="_plots"
                   :showSymbols="_showSymbols">
        </BokehPlot>
    </AnalysisCard>
</template>
