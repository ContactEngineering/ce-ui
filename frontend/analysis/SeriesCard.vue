<script setup>

import axios from "axios";
import {v4 as uuid4} from 'uuid';
import {computed, onMounted, ref} from "vue";

import {BDropdownDivider, BDropdownItem} from 'bootstrap-vue-next';

import AnalysisCard from "./AnalysisCard.vue";
import BokehPlot from '../components/BokehPlot.vue';

const props = defineProps({
    apiUrl: {
        type: String,
        default: '/analysis/api/card/series'
    },
    detailUrl: {
        type: String,
        default: '/ui/html/analysis-detail/'
    },
    enlarged: {
        type: Boolean,
        default: true
    },
    functionId: Number,
    functionName: String,
    subjects: String,
    uid: {
        type: String,
        default() {
            return uuid4();
        }
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

function updateCard() {
    /* Fetch JSON describing the card */
    _nbPendingAjaxRequests.value++;
    axios.get(`${props.apiUrl}/${props.functionId}?subjects=${props.subjects}`)
        .then(response => {
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
            _nbPendingAjaxRequests.value--;
        });
}

</script>

<template>
    <AnalysisCard v-model:analyses="_analyses"
                  :detailUrl="detailUrl"
                  :dois="_dois"
                  :enlarged="enlarged"
                  :messages="_messages"
                  :functionId="functionId"
                  :subjects="subjects"
                  :showLoadingSpinner="_nbPendingAjaxRequests > 0"
                  :title="_title"
                  @allTasksFinished="updateCard"
                  @someTasksFinished="updateCard"
                  @refreshButtonClicked="updateCard">
        <template #dropdowns>
            <BDropdownDivider></BDropdownDivider>
            <BDropdownItem :href="`/analysis/download/${analysisIds}/txt`">
                Download TXT
            </BDropdownItem>
            <BDropdownItem :href="`/analysis/download/${analysisIds}/csv`">
                Download CSV
            </BDropdownItem>
            <BDropdownItem :href="`/analysis/download/${analysisIds}/xlsx`">
                Download XLSX
            </BDropdownItem>
            <BDropdownItem @click="$refs.plot.download()">
                Download SVG
            </BDropdownItem>
        </template>
        <BokehPlot v-model:nbPendingAjaxRequests="_nbPendingAjaxRequests"
                   :plots="_plots"
                   :categories="_categories"
                   :dataSources="_dataSources"
                   :outputBackend="_outputBackend"
                   :showSymbols="_showSymbols"
                   :functionTitle="_title">
        </BokehPlot>
    </AnalysisCard>
</template>
