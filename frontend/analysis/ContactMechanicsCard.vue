<script setup lang="ts">

import { computed, onMounted, ref } from "vue";

import {
    QItem,
    QItemSection,
    QSeparator,
    QSpinner,
    QTabs,
    QTab,
    QTabPanels,
    QTabPanel,
    QBtn,
    QBanner
} from "quasar";

import { useNotify } from "@/utils/notify";
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

const { show } = useNotify();

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
const _activeTab = ref('geometry');

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
            <QSeparator />
            <QItem clickable v-close-popup @click="_parametersVisible = true">
                <QItemSection>Parameters...</QItemSection>
            </QItem>
            <QSeparator />
            <QItem clickable v-close-popup :href="`/analysis/download/${analysisIds}/zip`">
                <QItemSection>Download ZIP</QItemSection>
            </QItem>
            <QItem clickable v-close-popup @click="$refs.plot.download()">
                <QItemSection>Download SVG</QItemSection>
            </QItem>
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
                <QBanner v-if="_selection == null && !_isLoading" class="bg-info text-white">
                    Select a point in the graphs on the left for more details.
                </QBanner>
                <div v-if="_isLoading" class="flex justify-center q-mt-lg">
                    <div class="column items-center">
                        <QSpinner size="lg" />
                        <p class="q-mt-sm">Loading...</p>
                    </div>
                </div>
                <div v-if="_selection != null && !_isLoading">
                    <QTabs v-model="_activeTab" dense align="left" class="text-grey" active-color="primary" indicator-color="primary">
                        <QTab name="geometry" label="Contact geometry" />
                        <QTab name="pressure" label="Contact pressure" />
                        <QTab name="displacement" label="Displacement" />
                        <QTab name="gap" label="Gap" />
                        <QTab name="pressure-dist" label="Pressure distribution" />
                        <QTab name="gap-dist" label="Gap distribution" />
                        <QTab name="cluster-dist" label="Cluster area distribution" />
                    </QTabs>

                    <QTabPanels v-model="_activeTab" animated>
                        <QTabPanel name="geometry">
                            <DeepZoomImage v-if="_selection != null"
                                           ref="contactingPoints"
                                           :folder-url="_selection.folder"
                                           :prefix="`${_selection.dataPath}/dzi/contacting-points/`">
                            </DeepZoomImage>
                            <div v-if="_selection != null" class="text-right q-mt-md">
                                <QBtn color="primary" label="Download PNG" @click="$refs.contactingPoints.download()" />
                            </div>
                        </QTabPanel>
                        <QTabPanel name="pressure">
                            <DeepZoomImage v-if="_selection != null"
                                           ref="pressure"
                                           :colorbar="true"
                                           :folder-url="_selection.folder"
                                           :prefix="`${_selection.dataPath}/dzi/pressure/`">
                            </DeepZoomImage>
                            <div v-if="_selection != null" class="text-right q-mt-md">
                                <QBtn color="primary" label="Download PNG" @click="$refs.pressure.download()" />
                            </div>
                        </QTabPanel>
                        <QTabPanel name="displacement">
                            <DeepZoomImage v-if="_selection != null"
                                           ref="displacement"
                                           :colorbar="true"
                                           :folder-url="_selection.folder"
                                           :prefix="`${_selection.dataPath}/dzi/displacement/`">
                            </DeepZoomImage>
                            <div v-if="_selection != null" class="text-right q-mt-md">
                                <QBtn color="primary" label="Download PNG" @click="$refs.displacement.download()" />
                            </div>
                        </QTabPanel>
                        <QTabPanel name="gap">
                            <DeepZoomImage v-if="_selection != null"
                                           ref="gap"
                                           :colorbar="true"
                                           :folder-url="_selection.folder"
                                           :prefix="`${_selection.dataPath}/dzi/gap/`">
                            </DeepZoomImage>
                            <div v-if="_selection != null" class="text-right q-mt-md">
                                <QBtn color="primary" label="Download PNG" @click="$refs.gap.download()" />
                            </div>
                        </QTabPanel>
                        <QTabPanel name="pressure-dist">
                            <BokehPlot v-if="_selection != null"
                                       :data-sources="distributionDataSources"
                                       :options-widgets='["layout", "lineWidth", "symbolSize"]'
                                       :output-backend="_outputBackend"
                                       :plots="pressureDistributionPlot">
                            </BokehPlot>
                        </QTabPanel>
                        <QTabPanel name="gap-dist">
                            <BokehPlot v-if="_selection != null"
                                       :data-sources="distributionDataSources"
                                       :options-widgets='["layout", "lineWidth", "symbolSize"]'
                                       :output-backend="_outputBackend"
                                       :plots="gapDistributionPlot">
                            </BokehPlot>
                        </QTabPanel>
                        <QTabPanel name="cluster-dist">
                            <BokehPlot v-if="_selection != null"
                                       :data-sources="distributionDataSources"
                                       :options-widgets='["layout", "lineWidth", "symbolSize"]'
                                       :output-backend="_outputBackend"
                                       :plots="clusterAreaDistributionPlot">
                            </BokehPlot>
                        </QTabPanel>
                    </QTabPanels>
                </div>
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
