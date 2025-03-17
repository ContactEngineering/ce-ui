<script setup lang="ts">

import axios from "axios";

import {computed, onMounted, ref} from "vue";

import {
    BButton,
    BButtonToolbar,
    BFormGroup,
    BFormInput,
    BFormSelect,
    BInputGroup,
    BListGroup,
    BModal,
    BOverlay,
    BPagination,
    useToastController
} from "bootstrap-vue-next";

import {useSelectionStore} from "../stores/selection";

import DatasetListRow from '../manager/DatasetListRow.vue';
import SelectionOffcanvas from "../base/SelectionOffcanvas.vue";

const {show} = useToastController();
const selection = useSelectionStore();

const props = defineProps({
    apiUrl: {
        type: String,
        default: "/manager/api/surface/"
    },
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
    {text: 'Date', value: 'date'},
    {text: 'Name', value: 'name'},
];
const sharingStatusFilterChoices = [
    {text: 'All accessible datasets', value: 'all'},
    {text: 'Unpublished datasets created by me', value: 'own'},
    {text: 'Unpublished datasets created by others', value: 'others'},
    {text: 'Published datasets', value: 'published'}
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

function getDatasets(offset: number = 0) {
    searchDelayTimer = null;
    _isLoading.value = true;
    _currentPage.value = offset / _pageSize.value + 1;
    let queryUrl = `${props.apiUrl}?offset=${offset}&limit=${_pageSize.value}`;
    queryUrl += `&order_by=${_orderBy.value}`;
    queryUrl += `&sharing_status=${_sharingStatus.value}`;
    if (_searchTerm != null) {
        queryUrl += `&search=${_searchTerm.value}`;
    }
    axios.get(queryUrl).then(response => {
        _nbDatasets.value = response.data.count;
        _nbDatasetsOnCurrentPage.value = Math.min(response.data.results.length, _pageSize.value);
        _nextUrl.value = response.data.next;
        _previousUrl.value = response.data.previous;
        _datasets.value = response.data.results;
        _isLoading.value = false;
    }).catch(error => {
        show?.({
            props: {
                title: "Error fetching datasets",
                body: error,
                variant: 'danger'
            }
        });
        _isLoading.value = false;
    });
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

function createSurface() {
    axios.post('/manager/api/surface/').then(response => {
        window.location.href = `/ui/dataset-detail/${response.data.id}/`;
    });
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
    <div class="row">
        <div class="col-8">
            <BFormGroup class="mb-2"
                        description="Search for digital surface twins by name or tags">
                <BInputGroup>
                    <BFormInput v-model="searchTerm"
                                placeholder="Type to start searching..."
                                type="search"/>
                    <BButton title="Tips for searching"
                             variant="light"
                             @click="_searchInfoModalVisible = true">
                        <i aria-hidden="true" class="fa fa-info-circle"></i>
                    </BButton>
                </BInputGroup>
            </BFormGroup>
        </div>
        <div class="col-4">
            <BFormGroup description="Filter results by sharing status">
                <BFormSelect v-model="_sharingStatus" :disabled="_isLoading"
                             :options="sharingStatusFilterChoices" class="form-control"
                             name="sharing_status"
                             @change="sharingStatusChanged">
                </BFormSelect>
            </BFormGroup>
        </div>
    </div>
    <BOverlay :show="_isLoading">
        <BButtonToolbar class="mb-2">
            <BPagination v-model="currentPage"
                         :disabled="_isLoading" :limit="9" :per-page="_pageSize"
                         :total-rows="_nbDatasets"
                         class="me-2 mb-0">
            </BPagination>
            <BInputGroup class="me-2" prepend="Page size">
                <BFormSelect v-model="pageSize" :disabled="_isLoading"
                             :options="[10, 25, 50, 100]">
                </BFormSelect>
            </BInputGroup>
            <BInputGroup class="me-2" prepend="Sort by">
                <BFormSelect v-model="orderBy" :disabled="_isLoading"
                             :options="orderByFilterChoices">
                </BFormSelect>
            </BInputGroup>
            <BButton v-if="selection.nbSelected === 0" class="me-2" variant="light"
                     disabled>
                No selected datasets
            </BButton>
            <BButton v-if="selection.nbSelected > 0" class="me-2" variant="warning"
                     :disabled="_isLoading"
                     @click="_selectionOffcanvasVisible = true">
                {{ selection.nbSelected }} datasets selected
            </BButton>
            <BButton v-if="isAnonymous" disabled
                     title="Please sign-in to use this feature"
                     variant="primary">
                Create new digital surface twin
            </BButton>
            <BButton v-if="!isAnonymous"
                     class="float-end"
                     :disabled="_isLoading"
                     variant="primary"
                     @click="createSurface">
                Create new digital surface twin
            </BButton>
        </BButtonToolbar>
        <BListGroup>
            <div v-for="dataset in _datasets" :key="dataset.id">{{ dataset.selected }}
            </div>
            <DatasetListRow v-for="dataset in _datasets" :key="dataset.id"
                            :dataset="dataset"
                            v-model:selected="selection.datasetIds">
            </DatasetListRow>
        </BListGroup>

        <div v-if="!_isLoading" class="mt-2">
            Showing {{ _nbDatasetsOnCurrentPage }} digital surface twins out of
            {{ _nbDatasets }}.
        </div>
    </BOverlay>
    <!-- Search Help Modal-->
    <BModal v-model="_searchInfoModalVisible"
            :ok-only="true"
            size="xl"
            title="Tips for searching">
        <p>Searching is performed over these fields:</p>
        <ul>
            <li>Names of surface and measurements</li>
            <li>Names of tags</li>
            <li>Descriptions of digital surface twins and measurements</li>
        </ul>

        <p>All texts in the search field is split into a list of tokens.
            Searching finds matches
            of the search expression among these tokens. You can build
            search
            expression from search terms
            as follows:</p>

        <table class="table table-bordered table-condensed">
            <thead class="thead-light">
            <tr>
                <th>Search result should list items with</th>
                <th>Search expression</th>
                <th>Comment</th>
            </tr>
            </thead>
            <tbody>
            <tr>
                <td>both <em>AFM</em> and <em>surface</em></td>
                <td><input readonly size="40" type="text"
                           value="AFM surface">
                </td>
                <td>text not inside quote marks will be interpreted as AND
                </td>
            </tr>
            <tr>
                <td>either <em>AFM</em> or <em>surface</em> or both</td>
                <td><input readonly size="40" type="text"
                           value="AFM OR surface"></td>
                <td>logical OR, least precedence</td>
            </tr>
            <tr>
                <td><em>AFM</em> but not <em>surface</em></td>
                <td><input readonly size="40" type="text"
                           value="AFM -surface">
                </td>
                <td>the logical not operator is written by using -, has
                    highest
                    precedence
                </td>
            </tr>
            <tr>
                <td>the phrase <em>AFM Surface</em></td>
                <td><input readonly size="40" type="text"
                           value='"AFM surface"'>
                </td>
                <td><em>AFM</em> and <em>surface</em> are found if next to
                    each
                    other
                </td>
            </tr>
            <tr>
                <td><em>AFM Surface</em> as a phrase and <em>imported</em>
                    somewhere else
                </td>
                <td><input readonly size="40"
                           type="text"
                           value='"AFM surface" imported'></td>
                <td></td>
            </tr>
            <tr>
                <td><em>AFM Surface</em> as a phrase and <em>imported</em>
                    but
                    not <em>material</em></td>
                <td><input readonly
                           size="40"
                           type="text" value='"AFM surface" imported -material'></td>
                <td>The above can also be combined. Parentheses are not
                    allowed,
                    all entries
                    are valid search expressions.
                </td>
            </tr>
            </tbody>
        </table>
    </BModal>
    <SelectionOffcanvas
        v-model:visible="_selectionOffcanvasVisible"
    ></SelectionOffcanvas>
</template>
