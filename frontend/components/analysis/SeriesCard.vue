<script setup lang="ts">

import axios from "axios";
import throttle from "lodash/throttle";
import { computed, onBeforeUnmount, onMounted, ref } from "vue";

import { BDropdownDivider, BDropdownItem, BFormCheckbox, useToast } from "bootstrap-vue-next";

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
import { buildReferenceDataSources, REFERENCE_DATASETS, referenceSurfaceOptions, selectedReferenceKeys } from "@/utils/referenceData";

import AnalysisCard from "@/components/analysis/AnalysisCard.vue";
import BokehPlot from "@/components/ui/BokehPlot.vue";

const toast = useToast();

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

// Reference data (fixed comparison curves, e.g. a consensus-study result).
// The user toggles each reference surface independently (none, one, or both
// at once) and optionally adds IQR bands as a single shared toggle, rather
// than checking each of the 2 surfaces' 3 curves (median, lower/upper IQR)
// independently.
const _availableReferenceDatasets = computed(() => REFERENCE_DATASETS[props.functionName] ?? []);
const _referenceSurfaces = computed(() => referenceSurfaceOptions(_availableReferenceDatasets.value));
const _selectedReferenceSurfaceKeys = ref<string[]>([]);
const _showReferenceIqr = ref(false);
const _selectedReferenceDatasetKeys = computed<string[]>(() => selectedReferenceKeys(
    _availableReferenceDatasets.value, _selectedReferenceSurfaceKeys.value, _showReferenceIqr.value));

function toggleReferenceSurface(surfaceKey: string) {
    const index = _selectedReferenceSurfaceKeys.value.indexOf(surfaceKey);
    if (index === -1) {
        _selectedReferenceSurfaceKeys.value = [..._selectedReferenceSurfaceKeys.value, surfaceKey];
    } else {
        _selectedReferenceSurfaceKeys.value = _selectedReferenceSurfaceKeys.value.filter(k => k !== surfaceKey);
    }
}

// Collapsed by default: with several reference datasets registered for one
// workflow, showing every checkbox unconditionally would clutter a card that
// most views of it never need to compare against anything.
const _showReferenceDatasets = ref(false);
// Merged in, rather than mutating `_dataSources`, so re-fetching the card's own
// data (`updateCard`) cannot lose a selection made in the meantime.
const _plottedDataSources = computed(() => {
    if (_dataSources.value == null || _availableReferenceDatasets.value.length === 0) {
        return _dataSources.value;
    }
    const plot = _plots.value?.[0];
    return [
        ..._dataSources.value,
        ...buildReferenceDataSources(
            _selectedReferenceDatasetKeys.value,
            props.functionName,
            _dataSources.value,
            plot?.xAxisLabel ?? null,
            plot?.yAxisLabel ?? null)
    ];
});


onMounted(() => {
    updateCard();
});

/* While a batch of tasks drains, every single task that finishes reports
   "some tasks finished". Rebuilding the card is expensive (the server
   re-serializes every analysis and the browser re-fetches every data series),
   so partial completions are coalesced into at most one refresh per interval;
   the final refresh comes from `allTasksFinished`, which is not throttled. */
const updateCardThrottled = throttle(updateCard, 10000, {leading: false, trailing: true});

onBeforeUnmount(() => {
    updateCardThrottled.cancel();
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
            toast.create({
                title: "Error fetching analysis result",
                body: error.message,
                variant: "danger"
            })?.show();
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
        toast.create({
            title: "Error preparing download",
            body: describeRequestError(error),
            variant: "danger"
        })?.show();
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
                  @someTasksFinished="updateCardThrottled">
        <template #dropdowns>
            <template v-if="_availableReferenceDatasets.length > 0">
                <BDropdownDivider></BDropdownDivider>
                <!-- Tucked into the burger menu rather than a standalone button: few users
                     need this, so it should not be a main control element on the card. -->
                <BDropdownItem @click="_showReferenceDatasets = !_showReferenceDatasets">
                    <i class="fa-solid fa-code-compare me-1"></i>
                    {{ _showReferenceDatasets ? 'Hide reference data' : 'Compare to reference data' }}
                </BDropdownItem>
            </template>
            <template v-if="hasData">
                <BDropdownDivider></BDropdownDivider>
                <BDropdownItem @click="downloadData('txt')">
                    Download TXT
                </BDropdownItem>
                <BDropdownItem @click="downloadData('csv')">
                    Download CSV
                </BDropdownItem>
                <BDropdownItem @click="_plot.download()">
                    <!-- The save format follows the Bokeh output backend -->
                    Download {{ _outputBackend === 'svg' ? 'SVG' : 'PNG' }}
                </BDropdownItem>
            </template>
        </template>
        <div v-if="_showReferenceDatasets && _availableReferenceDatasets.length > 0"
             class="bg-light p-3 rounded border mb-2 shadow-sm">
            <div class="small fw-bold text-secondary mb-1">Compare to STC consensus curve:</div>
            <div class="d-flex flex-wrap align-items-center gap-2">
                <span v-for="surface in _referenceSurfaces"
                      :key="surface.key"
                      class="badge rounded-pill cursor-pointer border user-select-none py-1 px-2"
                      :class="_selectedReferenceSurfaceKeys.includes(surface.key)
                          ? 'bg-primary text-white border-primary'
                          : 'bg-light text-dark border-secondary-subtle opacity-75'"
                      @click="toggleReferenceSurface(surface.key)">
                    {{ surface.label }}
                </span>
                <BFormCheckbox v-if="_selectedReferenceSurfaceKeys.length > 0"
                               v-model="_showReferenceIqr"
                               class="ms-2">
                    Show IQR range
                </BFormCheckbox>
            </div>
        </div>
        <BokehPlot ref="_plot"
                   v-model:nbPendingAjaxRequests="_nbPendingAjaxRequests"
                   :categories="_categories"
                   :dataSources="_plottedDataSources"
                   :functionTitle="_title"
                   :outputBackend="_outputBackend"
                   :plots="_plots"
                   :showSymbols="_showSymbols">
        </BokehPlot>
    </AnalysisCard>
</template>
