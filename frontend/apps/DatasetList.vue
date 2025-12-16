<script setup lang="ts">

import { computed, onMounted, ref } from "vue";

import {
    QBtn,
    QBtnDropdown,
    QInput,
    QList,
    QItem,
    QItemSection,
    QItemLabel,
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

function sharingStatusChanged() {
    getDatasets();
}

</script>

<template>
    <div class="row items-center q-col-gutter-sm q-mb-md">
        <div class="col">
            <QInput v-model="searchTerm"
                    placeholder="Search digital surface twins..."
                    type="search"
                    outlined
                    dense>
                <template v-slot:prepend>
                    <q-icon name="search" />
                </template>
                <template v-slot:append>
                    <QBtn flat round dense icon="info" size="sm" @click="_searchInfoModalVisible = true" />
                </template>
            </QInput>
        </div>
        <div>
            <QBtnDropdown flat dense
                          :disable="_isLoading"
                          :label="sharingStatusFilterChoices.find(o => o.value === _sharingStatus)?.label"
                          icon="filter_list">
                <QList>
                    <QItem v-for="option in sharingStatusFilterChoices"
                           :key="option.value"
                           clickable
                           v-close-popup
                           :active="_sharingStatus === option.value"
                           @click="_sharingStatus = option.value; sharingStatusChanged()">
                        <QItemSection>
                            <QItemLabel>{{ option.label }}</QItemLabel>
                        </QItemSection>
                    </QItem>
                </QList>
            </QBtnDropdown>
        </div>
        <div>
            <QBtn v-if="isAnonymous"
                  disable
                  color="primary"
                  icon="add"
                  label="New"
                  title="Please sign-in to create a digital surface twin" />
            <QBtn v-else
                  color="primary"
                  :disable="_isLoading"
                  icon="add"
                  label="New"
                  @click="createSurface" />
        </div>
    </div>
    <div class="relative-position">
        <QInnerLoading :showing="_isLoading" />
        <div class="row items-center q-gutter-sm q-mb-md">
            <QPagination v-model="currentPage"
                         :max="Math.ceil(_nbDatasets / _pageSize) || 1"
                         :disable="_isLoading"
                         :max-pages="9"
                         boundary-links
                         direction-links />
            <QBtnDropdown flat dense
                          :disable="_isLoading"
                          :label="`${_pageSize} per page`"
                          icon="format_list_numbered">
                <QList>
                    <QItem v-for="option in pageSizeOptions"
                           :key="option.value"
                           clickable
                           v-close-popup
                           :active="pageSize === option.value"
                           @click="pageSize = option.value">
                        <QItemSection>
                            <QItemLabel>{{ option.label }} per page</QItemLabel>
                        </QItemSection>
                    </QItem>
                </QList>
            </QBtnDropdown>
            <QBtnDropdown flat dense
                          :disable="_isLoading"
                          :label="`Sort: ${orderByFilterChoices.find(o => o.value === _orderBy)?.label}`"
                          icon="sort">
                <QList>
                    <QItem v-for="option in orderByFilterChoices"
                           :key="option.value"
                           clickable
                           v-close-popup
                           :active="orderBy === option.value"
                           @click="orderBy = option.value">
                        <QItemSection>
                            <QItemLabel>{{ option.label }}</QItemLabel>
                        </QItemSection>
                    </QItem>
                </QList>
            </QBtnDropdown>
            <div class="col-grow" />
            <QBtn v-if="selection.nbSelected === 0"
                  flat
                  disable
                  icon="check_box_outline_blank"
                  label="No selected" />
            <QBtn v-if="selection.nbSelected > 0"
                  color="warning"
                  :disable="_isLoading"
                  icon="check_box"
                  :label="`${selection.nbSelected} selected`"
                  @click="_selectionOffcanvasVisible = true" />
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
