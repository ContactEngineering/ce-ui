<script setup lang="ts">

import axios from "axios";
import { computed, onMounted, ref } from "vue";

import { BDropdownDivider, BDropdownItem, useToastController } from "bootstrap-vue-next";

import { subjectsToBase64 } from "@/utils/api";
import {
    buildSeriesCsvRows,
    buildSeriesTxt,
    describeRequestError,
    seriesFromDataSource,
    slugifyFilename,
    toCsvText,
    triggerBrowserDownload
} from "@/utils/download";

import AnalysisCard from "@/components/analysis/AnalysisCard.vue";
import BokehPlot from "@/components/ui/BokehPlot.vue";

const { show } = useToastController();

const props = defineProps({
    apiUrl: {
        type: String,
        default: "/analysis/api/card/series"
    },
    detailUrl: {
        type: String,
        default: "/ui/analysis-detail/"
    },
    description: {
        type: String,
        default: null
    },
    enlarged: {
        type: Boolean,
        default: true
    },
    functionName: {
        type: String,
        required: true
    },
    referenceUrl: {
        type: String,
        default: null
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
const _plot = ref(null);

// Auxiliary information
const _dois = ref([]);
const _messages = ref([]);


onMounted(() => {
    updateCard();
});

const hasData = computed(() => {
    return _dataSources.value != null && _dataSources.value.length > 0;
});

function updateCard() {
    /* Fetch JSON describing the card */
    _nbPendingAjaxRequests.value++;
    axios.get(`${props.apiUrl}/${props.functionName}?subjects=${subjectsToBase64(props.subjects)}`)
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
        })
        .catch(error => {
            show?.({
                props: {
                    title: "Error fetching analysis result",
                    body: error.message,
                    variant: "danger"
                }
            });
        })
        .finally(() => {
            _nbPendingAjaxRequests.value--;
        });
}

/* Download the plotted data as a text or CSV file.

   The data series themselves live in the object store and are fetched straight from there, in the same way the plot
   fetches them. We convert them here rather than asking the server for a converted file, which would mean reading every
   series back out of the object store inside the request. */
async function downloadData(fileFormat) {
    const dataSources = _dataSources.value;
    if (dataSources == null || dataSources.length === 0) {
        return;
    }

    const plot = _plots.value[0];
    const basename = slugifyFilename(_title.value);

    _nbPendingAjaxRequests.value++;
    try {
        const responses = await Promise.all(dataSources.map(dataSource => axios.get(dataSource.url)));
        const series = dataSources.map(
            (dataSource, index) => seriesFromDataSource(dataSource, responses[index].data));

        if (fileFormat === "csv") {
            triggerBrowserDownload(
                `${basename}.csv`,
                toCsvText(buildSeriesCsvRows(series, plot.xAxisLabel, plot.yAxisLabel)),
                "text/csv;charset=utf-8");
        } else {
            triggerBrowserDownload(
                `${basename}.txt`,
                buildSeriesTxt(series, {
                    title: _title.value,
                    xLabel: plot.xAxisLabel,
                    yLabel: plot.yAxisLabel,
                    dois: _dois.value
                }),
                "text/plain;charset=utf-8");
        }
    } catch (error) {
        show?.({
            props: {
                title: "Error preparing download",
                body: describeRequestError(error),
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
                  :description="description"
                  :detailUrl="detailUrl"
                  :dois="_dois"
                  :enlarged="enlarged"
                  :functionName="functionName"
                  :messages="_messages"
                  :referenceUrl="referenceUrl"
                  :showLoadingSpinner="_nbPendingAjaxRequests > 0"
                  :subjects="subjects"
                  :title="_title"
                  @allTasksFinished="updateCard"
                  @refreshButtonClicked="updateCard"
                  @someTasksFinished="updateCard">
        <template #dropdowns>
            <template v-if="hasData">
                <BDropdownDivider></BDropdownDivider>
                <BDropdownItem @click="downloadData('txt')">
                    Download TXT
                </BDropdownItem>
                <BDropdownItem @click="downloadData('csv')">
                    Download CSV
                </BDropdownItem>
                <BDropdownItem @click="_plot.download()">
                    Download SVG
                </BDropdownItem>
            </template>
        </template>
        <BokehPlot ref="_plot"
                   v-model:nbPendingAjaxRequests="_nbPendingAjaxRequests"
                   :categories="_categories"
                   :dataSources="_dataSources"
                   :functionTitle="_title"
                   :outputBackend="_outputBackend"
                   :plots="_plots"
                   :showSymbols="_showSymbols">
        </BokehPlot>
    </AnalysisCard>
</template>
