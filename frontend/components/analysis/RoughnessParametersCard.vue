<script setup lang="ts">

import axios from "axios";
import { computed, onMounted, ref } from "vue";

import { BDropdownDivider, BDropdownItem, useToastController } from "bootstrap-vue-next";

import DataTable from "datatables.net-vue3";
import DataTablesLib from "datatables.net-bs5";

DataTable.use(DataTablesLib);

import { formatExponential } from "@/utils/formatting";
import { subjectsToBase64 } from "@/utils/api";
import { buildTableCsvRows, slugifyFilename, toCsvText, triggerBrowserDownload } from "@/utils/download";
import { escapeHtml } from "@/utils/html";

import AnalysisCard from "@/components/analysis/AnalysisCard.vue";

const {show} = useToastController();

const props = defineProps({
    apiUrl: {
        type: String,
        default: "/plugins/statistics/card/roughness-parameters"
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
    },
});

// Displayed data
const _analyses = ref(null);
const _columnDefs = ref([
    // Indicate that first column contains HTML
    // to have HTML tags removed for sorting/filtering
    { targets: 0, type: "html" }
]);
const _columns = ref([
    {
        title: "Measurement",
        render: function(data, type, row) {
            // `topography_name` and `topography_url` are user-controlled and must be escaped to prevent XSS.
            const name = escapeHtml(row.topography_name);
            // Encode the URL and escape it for safe use inside the attribute value.
            const url = escapeHtml(encodeURI(row.topography_url == null ? "" : row.topography_url));
            return `<a target="_blank" title="${name}" href="${url}">${name}</a>`;
        }
    },
    { data: "quantity", title: "Quantity" },
    { data: "from", title: "From" },
    { data: "symbol", title: "Symbol" },
    { data: "direction", title: "Direction" },
    {
        data: "value", title: "Value", render: function(x) {
            return formatExponential(x, 5);
        }
    },
    { data: "unit", title: "Unit" }
]);
const _dois = ref([]);
const _data = ref([]);
const _messages = ref([]);

// GUI logic
const _title = "Roughness parameters";
const _nbPendingAjaxRequests = ref(0);

onMounted(() => {
    updateCard();
});

const hasData = computed(() => {
    return _data.value != null && _data.value.length > 0;
});

/* Download the table as a CSV file. The table is fully client-side already, so nothing needs to be fetched. The
   measurement column renders a link and therefore carries no plain value; it is added back explicitly from the
   underlying row data. */
function downloadCsv() {
    triggerBrowserDownload(
        `${slugifyFilename(_title)}.csv`,
        toCsvText(buildTableCsvRows(_data.value, _columns.value,
                                    [{ title: "Measurement", data: "topography_name" }])),
        "text/csv;charset=utf-8");
}

function updateCard() {
    /* Fetch JSON describing the card */
    _nbPendingAjaxRequests.value++;
    axios.get(`${props.apiUrl}/${props.functionName}?subjects=${subjectsToBase64(props.subjects)}`)
        .then(response => {
            _analyses.value = response.data.analyses;
            /** replace null in value with NaN
             * This is needed because we cannot pass NaN through JSON without
             * extra libraries, so it is passed as null (workaround) */
            _data.value = response.data.tableData.map(x => {
                if (x["value"] === null) {
                    x["value"] = NaN;
                }
                return x;
            });
            _dois.value = response.data.dois;
            _messages.value = response.data.messages;
        })
        .catch(error => {
            show?.({
                props: {
                    title: "Error fetching roughness parameters",
                    body: error.message,
                    variant: "danger"
                }
            });
        })
        .finally(() => {
            _nbPendingAjaxRequests.value--;
        });
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
                <BDropdownItem @click="downloadCsv()">
                    Download CSV
                </BDropdownItem>
            </template>
        </template>
        <DataTable :column-defs="_columnDefs"
                   :columns="_columns"
                   :data="_data"
                   class="table table-striped table-bordered"
                   responsive="yes"
                   scroll-x="yes">
        </DataTable>
    </AnalysisCard>
</template>
