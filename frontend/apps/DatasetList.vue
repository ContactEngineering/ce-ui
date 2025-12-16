<script setup lang="ts">

import { computed, onMounted, ref } from "vue";

import {
    QBtn,
    QInput,
    QSelect,
    QList,
    QDialog,
    QCard,
    QCardSection,
    QCardActions,
    QInnerLoading,
    QPagination,
    QMarkupTable
} from "quasar";

import { useNotify } from "@/utils/notify";
import { managerApiSurfaceList, managerApiSurfaceCreate } from "@/api";

import { useDatasetSelectionStore } from "../stores/datasetSelection";

import DatasetListRow from '../manager/DatasetListRow.vue';
import SelectionOffcanvas from "../base/SelectionOffcanvas.vue";

const { show } = useNotify();
const selection = useDatasetSelectionStore();

const props = defineProps({
    currentPage: {
        Number,
        default: 0
    },
    isAnonymous: Boolean,
    pageSize: {
        type: Number,
        default: 10
    },
    searchTerm: {
        type: String,
        default: ""
    },
    searchDelay: {
        type: Number,
        default: 300
    }
});

// Constants
const orderByFilterChoices = [
    { label: 'Date', value: 'date' },
    { label: 'Name', value: 'name' },
];
const sharingStatusFilterChoices = [
    { label: 'All accessible datasets', value: 'all' },
    { label: 'Unpublished datasets created by me', value: 'own' },
    { label: 'Unpublished datasets created by others', value: 'others' },
    { label: 'Published datasets', value: 'published' }
];
const pageSizeOptions = [
    { label: '10', value: 10 },
    { label: '25', value: 25 },
    { label: '50', value: 50 },
    { label: '100', value: 100 }
];


// UI logic
const _currentPage = ref<number>(props.currentPage);
const _isLoading = ref<boolean>(false);
const _nbDatasets = ref<number>(null);
const _nbDatasetsOnCurrentPage = ref<number>(null);
const _orderBy = ref(orderByFilterChoices[0].value);
const _pageSize = ref<number>(props.pageSize);
const _searchTerm = ref<string>(props.searchTerm);
const _searchInfoModalVisible = ref<boolean>(false);
const _selectionOffcanvasVisible = ref<boolean>(false);
const _sharingStatus = ref(sharingStatusFilterChoices[0].value);

const _datasets = ref([]);
const _nextUrl = ref(null);
const _previousUrl = ref(null);

let searchDelayTimer = null;

async function getDatasets(offset: number = 0) {
    searchDelayTimer = null;
    _isLoading.value = true;
    _currentPage.value = offset / _pageSize.value + 1;
    try {
        // Note: order_by, sharing_status, and search are not in the OpenAPI schema
        // but are supported by the backend. Using type assertion to pass them.
        const response = await managerApiSurfaceList({
            query: {
                offset,
                limit: _pageSize.value,
                order_by: _orderBy.value,
                sharing_status: _sharingStatus.value,
                search: _searchTerm.value || undefined
            } as any
        });
        _nbDatasets.value = response.data.count;
        _nbDatasetsOnCurrentPage.value = Math.min(response.data.results.length, _pageSize.value);
        _nextUrl.value = response.data.next;
        _previousUrl.value = response.data.previous;
        _datasets.value = response.data.results;
    } catch (error) {
        show?.({
            props: {
                title: "Error fetching datasets",
                body: error,
                variant: 'danger'
            }
        });
    } finally {
        _isLoading.value = false;
    }
}

onMounted(() => {
    getDatasets();
});

const currentPage = computed({
    get() {
        return _currentPage.value;
    },
    set(value) {
        getDatasets((value - 1) * _pageSize.value);
    }
});

const orderBy = computed({
    get() {
        return _orderBy.value;
    },
    set(value) {
        _orderBy.value = value;
        getDatasets();
    }
});

const pageSize = computed({
    get() {
        return _pageSize.value;
    },
    set(value) {
        _pageSize.value = value;
        getDatasets();
    }
});

const searchTerm = computed({
    get() {
        if (_searchTerm.value.length === 0) {
            return null;
        }
        return _searchTerm.value;
    },
    set(value) {
        _searchTerm.value = value;
        clearTimeout(searchDelayTimer);
        searchDelayTimer = setTimeout(getDatasets, props.searchDelay);
    }
});

async function createSurface() {
    const response = await managerApiSurfaceCreate();
    window.location.href = `/ui/dataset-detail/${response.data.id}/`;
}

function select(dataset) {
    selection.select(dataset);
}

function unselect(dataset) {
    selection.unselect(dataset.id);
}

function sharingStatusChanged() {
    getDatasets();
}

</script>

<template>
    <div class="row q-mb-md">
        <div class="col-8">
            <QInput v-model="searchTerm"
                    placeholder="Type to start searching..."
                    type="search"
                    outlined
                    dense
                    hint="Search for digital surface twins by name or tags">
                <template v-slot:append>
                    <QBtn flat round icon="info" @click="_searchInfoModalVisible = true" />
                </template>
            </QInput>
        </div>
        <div class="col-4">
            <QSelect v-model="_sharingStatus"
                     :options="sharingStatusFilterChoices"
                     :disable="_isLoading"
                     emit-value
                     map-options
                     outlined
                     dense
                     hint="Filter results by sharing status"
                     @update:model-value="sharingStatusChanged" />
        </div>
    </div>
    <div class="relative-position">
        <QInnerLoading :showing="_isLoading" />
        <div class="flex items-center q-gutter-sm q-mb-md flex-wrap">
            <QPagination v-model="currentPage"
                         :max="Math.ceil(_nbDatasets / _pageSize) || 1"
                         :disable="_isLoading"
                         :max-pages="9"
                         boundary-links
                         direction-links />
            <div class="flex items-center q-gutter-xs">
                <span class="text-caption">Page size:</span>
                <QSelect v-model="pageSize"
                         :options="pageSizeOptions"
                         :disable="_isLoading"
                         emit-value
                         map-options
                         outlined
                         dense
                         style="min-width: 80px" />
            </div>
            <div class="flex items-center q-gutter-xs">
                <span class="text-caption">Sort by:</span>
                <QSelect v-model="orderBy"
                         :options="orderByFilterChoices"
                         :disable="_isLoading"
                         emit-value
                         map-options
                         outlined
                         dense
                         style="min-width: 100px" />
            </div>
            <QBtn v-if="selection.nbSelected === 0"
                  flat
                  disable
                  label="No selected datasets" />
            <QBtn v-if="selection.nbSelected > 0"
                  color="warning"
                  :disable="_isLoading"
                  :label="`${selection.nbSelected} datasets selected`"
                  @click="_selectionOffcanvasVisible = true" />
            <QBtn v-if="isAnonymous"
                  disable
                  color="primary"
                  label="Create new digital surface twin"
                  title="Please sign-in to use this feature" />
            <QBtn v-if="!isAnonymous"
                  color="primary"
                  :disable="_isLoading"
                  label="Create new digital surface twin"
                  @click="createSurface" />
        </div>
        <QList bordered separator>
            <DatasetListRow v-for="dataset in _datasets"
                            :key="dataset.id"
                            :dataset="dataset"
                            v-model:selected="selection.datasetIds" />
        </QList>

        <div v-if="!_isLoading" class="q-mt-md text-caption">
            Showing {{ _nbDatasetsOnCurrentPage }} digital surface twins out of {{ _nbDatasets }}.
        </div>
    </div>
    <!-- Search Help Modal-->
    <QDialog v-model="_searchInfoModalVisible">
        <QCard style="min-width: 700px; max-width: 900px">
            <QCardSection>
                <div class="text-h6">Tips for searching</div>
            </QCardSection>
            <QCardSection>
                <p>Searching is performed over these fields:</p>
                <ul>
                    <li>Names of surface and measurements</li>
                    <li>Names of tags</li>
                    <li>Descriptions of digital surface twins and measurements</li>
                </ul>

                <p>All texts in the search field is split into a list of tokens.
                    Searching finds matches of the search expression among these tokens.
                    You can build search expression from search terms as follows:</p>

                <QMarkupTable>
                    <thead>
                    <tr>
                        <th class="text-left">Search result should list items with</th>
                        <th class="text-left">Search expression</th>
                        <th class="text-left">Comment</th>
                    </tr>
                    </thead>
                    <tbody>
                    <tr>
                        <td>both <em>AFM</em> and <em>surface</em></td>
                        <td><code>AFM surface</code></td>
                        <td>text not inside quote marks will be interpreted as AND</td>
                    </tr>
                    <tr>
                        <td>either <em>AFM</em> or <em>surface</em> or both</td>
                        <td><code>AFM OR surface</code></td>
                        <td>logical OR, least precedence</td>
                    </tr>
                    <tr>
                        <td><em>AFM</em> but not <em>surface</em></td>
                        <td><code>AFM -surface</code></td>
                        <td>the logical not operator is written by using -, has highest precedence</td>
                    </tr>
                    <tr>
                        <td>the phrase <em>AFM Surface</em></td>
                        <td><code>"AFM surface"</code></td>
                        <td><em>AFM</em> and <em>surface</em> are found if next to each other</td>
                    </tr>
                    <tr>
                        <td><em>AFM Surface</em> as a phrase and <em>imported</em> somewhere else</td>
                        <td><code>"AFM surface" imported</code></td>
                        <td></td>
                    </tr>
                    <tr>
                        <td><em>AFM Surface</em> as a phrase and <em>imported</em> but not <em>material</em></td>
                        <td><code>"AFM surface" imported -material</code></td>
                        <td>The above can also be combined. Parentheses are not allowed, all entries are valid search expressions.</td>
                    </tr>
                    </tbody>
                </QMarkupTable>
            </QCardSection>
            <QCardActions align="right">
                <QBtn flat label="Close" v-close-popup />
            </QCardActions>
        </QCard>
    </QDialog>
    <SelectionOffcanvas v-model:visible="_selectionOffcanvasVisible" />
</template>
