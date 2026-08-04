<script setup lang="ts">

import axios from "axios";
import throttle from "lodash/throttle";
import { computed, onBeforeUnmount, onMounted, ref } from "vue";

import { BDropdownDivider, BDropdownItem, BTab, BTabs, useToastController } from "bootstrap-vue-next";

import { useActiveTab } from "@/stores/tabs";

import { subjectsToBase64 } from "@/utils/api";
import {
    buildColumnsCsvRows,
    describeRequestError,
    toCsvText,
    triggerBrowserDownload
} from "@/utils/download";

import AnalysisCard from "@/components/analysis/AnalysisCard.vue";
import ContactMechanicsParametersModal from "@/components/analysis/ContactMechanicsParametersModal.vue";
import BokehPlot from "@/components/ui/BokehPlot.vue";
import DeepZoomImagePanel from "@/components/ui/DeepZoomImagePanel.vue";
import DownloadModal from "@/components/ui/DownloadModal.vue";
import LoadingIndicator from "@/components/ui/LoadingIndicator.vue";

const props = defineProps({
    apiUrl: {
        type: String,
        default: "/plugins/contact/card/contact-mechanics"
    },
    detailUrl: {
        type: String,
        default: '/ui/analysis-detail/'
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

const { show } = useToastController();

const _analyses = ref(null);
let _analysesById = {};
const _api = ref({});
const _dois = ref([]);
const _dataSources = ref([]);
const _functionKwargs = ref(null);
const _limitsToFunctionKwargs = ref(null);
const _outputBackend = ref("svg");
const _selection = ref(null);
const _isLoading = ref(false);

// GUI logic
const _nbPendingAjaxRequests = ref(0);
const _parametersVisible = ref(false);
const _plot = ref(null);
const _downloadModal = ref(null);
// Which result of the selected step is shown; survives a page reload and
// picking another point in the contact-mechanics plot
const activeTab = useActiveTab("contact-mechanics-card");

onMounted(() => {
    updateCard();
});

/* While a batch of tasks drains, every single task that finishes reports
   "some tasks finished". Rebuilding the card is expensive (the server
   re-serializes every analysis and the browser re-fetches every data series),
   so partial completions are coalesced into at most one refresh per interval;
   the final refresh comes from `allTasksFinished`, which is not throttled. */
const updateCardThrottled = throttle(() => updateCard(), 10000, {leading: false, trailing: true});

onBeforeUnmount(() => {
    updateCardThrottled.cancel();
});

function updateCard() {
    /* Fetch JSON describing the card */
    let functionKwargsBase64 = btoa(JSON.stringify(_functionKwargs.value));
    _nbPendingAjaxRequests.value++;
    axios.get(`${props.apiUrl}/${props.functionName}?subjects=${subjectsToBase64(props.subjects)}&function_kwargs=${functionKwargsBase64}`)
        .then(response => {
            _analyses.value = response.data.analyses;
            _analysesById = {};
            for (const analysis of response.data.analyses) {
                _analysesById[analysis.id] = analysis;
            }
            _dois.value = response.data.dois;
            if (_functionKwargs.value === null) {
                _functionKwargs.value = response.data.unique_kwargs;
            } else {
                _functionKwargs.value = {
                    ..._functionKwargs.value,
                    ...response.data.unique_kwargs  // override since the server may report changes
                };
            }
            _limitsToFunctionKwargs.value = response.data.limitsToFunctionKwargs;
            _api.value = response.data.api;

            _dataSources.value = response.data.plotConfiguration?.dataSources;
            _outputBackend.value = response.data.plotConfiguration?.outputBackend;
        })
        .catch(error => {
            show?.({
                props: {
                    title: "Error fetching contact mechanics analysis results",
                    body: error.message,
                    variant: "danger"
                }
            });
        })
        .finally(() => {
            _nbPendingAjaxRequests.value--;
        });
}

function onSelected(obj, data) {
    const name = data.source.name;
    const path = data.source.data.dataPath[data.source.selected.indices[0]];
    const analysisId = parseInt(name.split("-")[1]);
    const folder = _analysesById[analysisId].folder;
    _isLoading.value = true;
    axios.get(folder).then(response => {
        _isLoading.value = false;
        _selection.value = {
            analysisId: analysisId,
            dataPath: path,
            folder: folder,
            folderInventory: response.data
        };
    }).catch(error => {
        _isLoading.value = false;
        show?.({
            props: {
                title: "Error analysis results",
                body: error.message,
                variant: "danger"
            }
        });
    });
}

const contactMechanicsPlots = computed(() => {
    return [{
        title: "Contact area vs load",
        xData: data => data.mean_pressures,
        yData: data => data.total_contact_areas,
        auxiliaryDataColumns: {
            dataPath: "data_paths"
        },
        alphaData: data => data.converged.map(value => value ? 1.0 : 0.3),
        xAxisLabel: "$$p/E^*$$",
        yAxisLabel: "$$A/A_0$$",
        xAxisType: "log",
        yAxisType: "log"
    }, {
        title: "Load vs displacement",
        xData: data => data.mean_gaps,
        yData: data => data.mean_pressures,
        auxiliaryDataColumns: {
            dataPath: "data_paths"
        },
        alphaData: data => data.converged.map(value => value ? 1.0 : 0.3),
        xAxisLabel: "$$u/h_\\text{rms}$$",
        yAxisLabel: "$$p/E^*$$",
        xAxisType: "linear",
        yAxisType: "log"
    }];
});

const contactMechanicsCategories = computed(() => {
    return [{ key: "subjectName", title: "Measurements" }];
});

const pressureDistributionPlot = computed(() => {
    return [{
        title: "Pressure",
        xData: data => data.pressure,
        yData: data => data.pressureProbabilityDensity,
        xAxisLabel: "$$p\\text{ (}E^*\\text{)}$$",
        yAxisLabel: "$$P(p)\\text{ (}E^{*-1}\\text{)}$$"
    }];
});

const gapDistributionPlot = computed(() => {
    return [{
        title: "Gap",
        xData: data => data.gap.map(value => data.gapSIScaleFactor * value),
        yData: data => data.gapProbabilityDensity.map(value => data.gapProbabilityDensitySIScaleFactor * value),
        xAxisLabel: "$$g\\text{ (m)}$$",
        yAxisLabel: "$$P(g)\\text{ (m}^{-1}\\text{)}$$"
    }];
});

const clusterAreaDistributionPlot = computed(() => {
    return [{
        title: "Cluster area",
        xData: data => data.clusterArea.map(value => data.clusterAreaSIScaleFactor * value),
        yData: data => data.clusterAreaProbabilityDensity.map(
            value => data.clusterAreaProbabilityDensitySIScaleFactor * value),
        xAxisLabel: "$$A\\text{ (m}^2\\text{)}$$",
        yAxisLabel: "$$P(A)\\text{ (m}^{-2}\\text{)}$$"
    }];
});

const distributionDataSources = computed(() => {
    const fn = `${_selection.value.dataPath}/json/distributions.json`;
    return [{
        url: _selection.value.folderInventory[fn].file
    }];
});

const analysisIds = computed(() => {
    if (_analyses.value == null) {
        return [];
    }
    return Object.entries(_analyses.value).map(([key, a]) => a.id).join();
});

const hasData = computed(() => {
    return _dataSources.value != null && _dataSources.value.length > 0;
});

/* Columns of the summary data, i.e. of what the two plots of this card show. These are the keys of the result of a
   contact mechanics calculation, one entry per calculation step. */
const SUMMARY_COLUMNS = [
    { key: "mean_pressures", title: "Normalized pressure p/E*" },
    { key: "total_contact_areas", title: "Fractional contact area A/A0" },
    { key: "mean_gaps", title: "Normalized mean gap u/h_rms" },
    { key: "converged", title: "Converged" },
    { key: "data_paths", title: "Directory of the detailed results" }
];

/* Download the summary data of the plots as a CSV file. This is the data the card has already fetched from the object
   store, so no server-side conversion is involved. The maps of the individual calculation steps are much larger and are
   bundled server-side instead, see `downloadZip`. */
async function downloadCsv() {
    const dataSources = _dataSources.value;
    if (dataSources == null || dataSources.length === 0) {
        return;
    }

    _nbPendingAjaxRequests.value++;
    try {
        const responses = await Promise.all(dataSources.map(dataSource => axios.get(dataSource.url)));
        const groups = dataSources.map((dataSource, index) => ({
            label: dataSource.subjectName,
            data: responses[index].data
        }));
        triggerBrowserDownload(
            "contact-mechanics.csv",
            toCsvText(buildColumnsCsvRows(groups, SUMMARY_COLUMNS, "Measurement")),
            "text/csv;charset=utf-8");
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

/* Download all result files as a ZIP archive.

   A contact mechanics result holds one NetCDF file per calculation step, each with maps of pressure, gap and
   displacement over the full grid, so an archive can be very large. Bundling therefore happens in a Celery worker; the
   modal reports its progress and starts the download once the archive is ready. */
function downloadZip() {
    if (analysisIds.value.length === 0) {
        return;
    }
    _downloadModal.value.download(
        `/analysis/v2/download-results/${analysisIds.value}/`,
        {title: "Download contact mechanics results"});
}

</script>

<template>
    <AnalysisCard v-model:analyses="_analyses"
                  :description="description"
                  :detailUrl="detailUrl"
                  :dois="_dois"
                  :enlarged="enlarged"
                  :functionName="functionName"
                  :referenceUrl="referenceUrl"
                  :showLoadingSpinner="_nbPendingAjaxRequests > 0"
                  :subjects="subjects"
                  title="Contact mechanics"
                  @allTasksFinished="updateCard"
                  @refreshButtonClicked="updateCard"
                  @someTasksFinished="updateCardThrottled">
        <template #dropdowns>
            <BDropdownDivider></BDropdownDivider>
            <BDropdownItem @click="_parametersVisible = true">
                Parameters...
            </BDropdownItem>
            <template v-if="hasData">
                <BDropdownDivider></BDropdownDivider>
                <BDropdownItem @click="downloadCsv()">
                    Download CSV
                </BDropdownItem>
                <BDropdownItem @click="downloadZip()">
                    Download ZIP
                </BDropdownItem>
                <BDropdownItem @click="_plot.download()">
                    <!-- The save format follows the Bokeh output backend -->
                    Download {{ _outputBackend === 'svg' ? 'SVG' : 'PNG' }}
                </BDropdownItem>
            </template>
        </template>
        <div class="row">
            <div :class="{ 'col-6': enlarged, 'col-12': !enlarged }">
                <BokehPlot
                    ref="_plot"
                    :categories="contactMechanicsCategories"
                    :data-sources="_dataSources"
                    :options-widgets="['layout', 'legend', 'lineWidth', 'symbolSize']"
                    :output-backend="_outputBackend"
                    :plots="contactMechanicsPlots"
                    :selectable="enlarged"
                    @selected="onSelected">
                </BokehPlot>
            </div>

            <!-- Right with simulation details and actions -->
            <div v-if="enlarged" class="col-6">
                <div v-if="_selection == null && !_isLoading" id="geometry" class="alert alert-secondary">
                    <i class="fa-solid fa-circle-info me-2"></i>Select a point
                    in the graphs on the left for more details.
                </div>
                <LoadingIndicator v-if="_isLoading"/>
                <BTabs v-if="_selection != null && !_isLoading" v-model="activeTab">
                    <BTab id="contact-geometry" title="Contact geometry">
                        <DeepZoomImagePanel :folder-url="_selection.folder"
                                            :prefix="`${_selection.dataPath}/dzi/contacting-points/`">
                        </DeepZoomImagePanel>
                    </BTab>
                    <BTab id="contact-pressure" title="Contact pressure">
                        <DeepZoomImagePanel :colorbar="true"
                                            :folder-url="_selection.folder"
                                            :prefix="`${_selection.dataPath}/dzi/pressure/`">
                        </DeepZoomImagePanel>
                    </BTab>
                    <BTab id="contact-displacement" title="Displacement">
                        <DeepZoomImagePanel :colorbar="true"
                                            :folder-url="_selection.folder"
                                            :prefix="`${_selection.dataPath}/dzi/displacement/`">
                        </DeepZoomImagePanel>
                    </BTab>
                    <BTab id="contact-gap" title="Gap">
                        <DeepZoomImagePanel :colorbar="true"
                                            :folder-url="_selection.folder"
                                            :prefix="`${_selection.dataPath}/dzi/gap/`">
                        </DeepZoomImagePanel>
                    </BTab>
                    <BTab id="contact-pressure-distribution" title="Pressure distribution">
                        <BokehPlot v-if="_selection != null"
                                   :data-sources="distributionDataSources"
                                   :options-widgets='["layout", "lineWidth", "symbolSize"]'
                                   :output-backend="_outputBackend"
                                   :plots="pressureDistributionPlot">
                        </BokehPlot>
                    </BTab>
                    <BTab id="contact-gap-distribution" title="Gap distribution">
                        <BokehPlot v-if="_selection != null"
                                   :data-sources="distributionDataSources"
                                   :options-widgets='["layout", "lineWidth", "symbolSize"]'
                                   :output-backend="_outputBackend"
                                   :plots="gapDistributionPlot">
                        </BokehPlot>
                    </BTab>
                    <BTab id="contact-cluster-area-distribution" title="Cluster area distribution">
                        <BokehPlot v-if="_selection != null"
                                   :data-sources="distributionDataSources"
                                   :options-widgets='["layout", "lineWidth", "symbolSize"]'
                                   :output-backend="_outputBackend"
                                   :plots="clusterAreaDistributionPlot">
                        </BokehPlot>
                    </BTab>
                </BTabs>
            </div>
        </div>
    </AnalysisCard>
    <DownloadModal ref="_downloadModal"></DownloadModal>
    <ContactMechanicsParametersModal v-if="_limitsToFunctionKwargs !== null && _functionKwargs !== null"
                                     v-model:kwargs="_functionKwargs"
                                     v-model:visible="_parametersVisible"
                                     :limits-to-function-kwargs="_limitsToFunctionKwargs"
                                     @updateKwargs="updateCard">
    </ContactMechanicsParametersModal>
</template>
