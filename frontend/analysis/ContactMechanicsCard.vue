<script setup lang="ts">

import { computed, onMounted, ref } from "vue";

import { BDropdownDivider, BDropdownItem, BSpinner, BTab, BTabs, useToastController } from "bootstrap-vue-next";

import { pluginsContactCardContactMechanicsRetrieve, filesFolderRetrieve } from "@/api";
import { subjectsToBase64, getIdFromUrl } from "@/utils/api";

import BokehPlot from "@/components/BokehPlot.vue";
import ContactMechanicsParametersModal from "@/analysis/ContactMechanicsParametersModal.vue";
import DeepZoomImage from "@/components/DeepZoomImage.vue";
import AnalysisCard from "@/analysis/AnalysisCard.vue";

const props = defineProps({
    apiUrl: {
        type: String,
        default: "/plugins/contact/card/contact-mechanics"
    },
    detailUrl: {
        type: String,
        default: '/ui/analysis-detail/'
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

onMounted(() => {
    updateCard();
});

async function updateCard() {
    /* Fetch JSON describing the card */
    let functionKwargsBase64 = btoa(JSON.stringify(_functionKwargs.value));
    _nbPendingAjaxRequests.value++;
    try {
        const response = await pluginsContactCardContactMechanicsRetrieve({
            path: {workflow: props.functionName},
            query: {
                subjects: subjectsToBase64(props.subjects),
                function_kwargs: functionKwargsBase64
            }
        } as any);
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
    } catch (error: any) {
        show?.({
            props: {
                title: "Error fetching contact mechanics analysis results",
                body: error.message,
                variant: "danger"
            }
        });
    } finally {
        _nbPendingAjaxRequests.value--;
    }
}

async function onSelected(obj, data) {
    const name = data.source.name;
    const path = data.source.data.dataPath[data.source.selected.indices[0]];
    const analysisId = parseInt(name.split("-")[1]);
    const folder = _analysesById[analysisId].folder;
    _isLoading.value = true;
    try {
        const folderId = getIdFromUrl(folder);
        const response = await filesFolderRetrieve({path: {id: folderId}});
        _selection.value = {
            analysisId: analysisId,
            dataPath: path,
            folder: folder,
            folderInventory: response.data
        };
    } catch (error: any) {
        show?.({
            props: {
                title: "Error analysis results",
                body: error.message,
                variant: "danger"
            }
        });
    } finally {
        _isLoading.value = false;
    }
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

</script>

<template>
    <AnalysisCard v-model:analyses="_analyses"
                  :detailUrl="detailUrl"
                  :dois="_dois"
                  :enlarged="enlarged"
                  :functionName="functionName"
                  :showLoadingSpinner="_nbPendingAjaxRequests > 0"
                  :subjects="subjects"
                  title="Contact mechanics"
                  @allTasksFinished="updateCard"
                  @refreshButtonClicked="updateCard"
                  @someTasksFinished="updateCard">
        <template #dropdowns>
            <BDropdownDivider></BDropdownDivider>
            <BDropdownItem @click="_parametersVisible = true">
                Parameters...
            </BDropdownItem>
            <BDropdownDivider></BDropdownDivider>
            <BDropdownItem :href="`/analysis/download/${analysisIds}/zip`">
                Download ZIP
            </BDropdownItem>
            <BDropdownItem @click="$refs.plot.download()">
                Download SVG
            </BDropdownItem>
        </template>
        <div class="row">
            <div :class="{ 'col-6': enlarged, 'col-12': !enlarged }">
                <BokehPlot
                    ref="plot"
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
                <div v-if="_selection == null && !_isLoading" id="geometry" class="alert alert-info">Select a point
                    in the graphs on the left for more details.
                </div>
                <div v-if="_isLoading"
                     class="d-flex justify-content-center mt-5">
                    <div class="flex-column text-center">
                        <b-spinner />
                        <p>Loading...</p>
                    </div>
                </div>
                <BTabs v-if="_selection != null && !_isLoading">
                    <BTab title="Contact geometry">
                        <DeepZoomImage v-if="_selection != null"
                                       ref="contactingPoints"
                                       :folder-url="_selection.folder"
                                       :prefix="`${_selection.dataPath}/dzi/contacting-points/`">
                        </DeepZoomImage>
                        <div v-if="_selection != null" class="pull-right">
                            <a class="btn btn-default btn-block btn-lg mt-3"
                               v-on:click="$refs.contactingPoints.download()">
                                Download PNG
                            </a>
                        </div>
                    </BTab>
                    <BTab title="Contact pressure">
                        <DeepZoomImage v-if="_selection != null"
                                       ref="pressure"
                                       :colorbar="true"
                                       :folder-url="_selection.folder"
                                       :prefix="`${_selection.dataPath}/dzi/pressure/`">
                        </DeepZoomImage>
                        <div v-if="_selection != null" class="pull-right">
                            <a class="btn btn-default btn-block btn-lg" v-on:click="$refs.pressure.download()">
                                Download PNG
                            </a>
                        </div>
                    </BTab>
                    <BTab title="Displacement">
                        <DeepZoomImage v-if="_selection != null"
                                       ref="displacement"
                                       :colorbar="true"
                                       :folder-url="_selection.folder"
                                       :prefix="`${_selection.dataPath}/dzi/displacement/`">
                        </DeepZoomImage>
                        <div v-if="_selection != null" class="pull-right">
                            <a class="btn btn-default btn-block btn-lg" v-on:click="$refs.displacement.download()">
                                Download PNG
                            </a>
                        </div>
                    </BTab>
                    <BTab title="Gap">
                        <DeepZoomImage v-if="_selection != null"
                                       ref="gap"
                                       :colorbar="true"
                                       :folder-url="_selection.folder"
                                       :prefix="`${_selection.dataPath}/dzi/gap/`">
                        </DeepZoomImage>
                        <div v-if="_selection != null" class="pull-right">
                            <a class="btn btn-default btn-block btn-lg" v-on:click="$refs.gap.download()">
                                Download PNG
                            </a>
                        </div>
                    </BTab>
                    <BTab title="Pressure distribution">
                        <BokehPlot v-if="_selection != null"
                                   :data-sources="distributionDataSources"
                                   :options-widgets='["layout", "lineWidth", "symbolSize"]'
                                   :output-backend="_outputBackend"
                                   :plots="pressureDistributionPlot">
                        </BokehPlot>
                    </BTab>
                    <BTab title="Gap distribution">
                        <BokehPlot v-if="_selection != null"
                                   :data-sources="distributionDataSources"
                                   :options-widgets='["layout", "lineWidth", "symbolSize"]'
                                   :output-backend="_outputBackend"
                                   :plots="gapDistributionPlot">
                        </BokehPlot>
                    </BTab>
                    <BTab title="Cluster area distribution">
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
    <ContactMechanicsParametersModal v-if="_limitsToFunctionKwargs !== null && _functionKwargs !== null"
                                     v-model:kwargs="_functionKwargs"
                                     v-model:visible="_parametersVisible"
                                     :limits-to-function-kwargs="_limitsToFunctionKwargs"
                                     @updateKwargs="updateCard">
    </ContactMechanicsParametersModal>
</template>
