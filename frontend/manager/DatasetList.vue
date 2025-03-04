<script setup>

import axios from "axios";

import {computed, onMounted, ref} from "vue";

import {
    BButton,
    BButtonGroup,
    BButtonToolbar,
    BFormGroup,
    BFormSelect,
    BInputGroup,
    BListGroup,
    BOverlay,
    BPagination,
    BToastOrchestrator,
    useToastController
} from "bootstrap-vue-next";

import Basket from './Basket.vue';
import DatasetListRow from './DatasetListRow.vue';

const {show} = useToastController();

const props = defineProps({
    apiUrl: {
        type: String,
        default: "/manager/api/surface/"
    },
    currentPage: Number,
    initialSelection: {
        type: Array,
        default: []
    },
    isAnonymous: Boolean,
    isLoading: Boolean,
    pageSize: Number,
    searchTerm: String
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
const _currentPage = ref(props.currentPage);
const _isLoading = ref(props.isLoading);
const _nbDatasets = ref(null);
const _nbDatasetsOnCurrentPage = ref(null);
const _orderBy = ref(orderByFilterChoices[0].value);
const _pageSize = ref(props.pageSize);
const _searchTerm = ref(props.searchTerm);
const _selection = ref(props.initialSelection);
const _sharingStatus = ref(sharingStatusFilterChoices[0].value);

const _datasets = ref([]);
const _nextUrl = ref(null);
const _previousUrl = ref(null);

function getDatasets(offset = 0) {
    _isLoading.value = true;
    _currentPage.value = offset / _pageSize.value + 1;
    let queryUrl = `${props.apiUrl}?offset=${offset}&limit=${_pageSize.value}`;
    queryUrl += `&order_by=${_orderBy.value}`;
    queryUrl += `&sharing_status=${_sharingStatus.value}`;
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

const searchUrl = computed(() => {
    // Returns URL object

    // replace page_size parameter
    // ref: https://usefulangle.com/post/81/javascript-change-url-parameters
    let queryParams = url.searchParams;

    queryParams.set("search", _searchTerm.value);  // empty string -> no search
    queryParams.set("order_by", _orderBy.value);
    queryParams.set("sharing_status", _sharingStatus.value);
    queryParams.set('page_size', _pageSize.value);
    queryParams.set('page', currentPage.value);
    url.search = queryParams.toString();

    return url;
});

function clearSearchTerm() {
    _searchTerm.value = '';
    getDatasets();
}

function createSurface() {
    axios.post('/manager/api/surface/').then(response => {
        window.location.href = `/ui/html/surface/?surface=${response.data.id}`;
    });
}

function select() {

}

function unselect() {

}

</script>

<template>
    <BToastOrchestrator></BToastOrchestrator>
    <Basket :basket-items="_selection" @unselect-successful="unselect">
    </Basket>
    <BOverlay :show="_isLoading">
        <div class="row row-cols-lg-auto">
            <BButtonToolbar class="mb-2">
                <BButtonGroup class="me-2"
                              v-if="_searchTerm">
                    <BButton variant="warning"
                             @click="clearSearchTerm"
                             :disabled="_isLoading">
                        Clear filter for <b>{{ _searchTerm }}</b>
                    </BButton>
                </BButtonGroup>
                <BButtonGroup class="me-2">
                    <BButton variant="outline-info"
                             disabled>
                        Not filtered for search term
                    </BButton>
                </BButtonGroup>
                <BFormGroup class="me-2">
                    <BFormSelect name="sharing_status" class="form-control"
                                 v-model="_sharingStatus" @change="getDatasets"
                                 :disabled="_isLoading"
                                 :options="sharingStatusFilterChoices">
                    </BFormSelect>
                </BFormGroup>

                <BButtonGroup v-if="isAnonymous">
                    <BButton variant="primary"
                             title="Please sign-in to use this feature"
                             disabled>
                        Create new digital surface twin
                    </BButton>
                </BButtonGroup>
                <BButtonGroup v-if="!isAnonymous">
                    <BButton variant="primary"
                             @click="createSurface"
                             :disabled="_isLoading">
                        Create new digital surface twin
                    </BButton>
                </BButtonGroup>
            </BButtonToolbar>
        </div>
        <div class="row row-cols-lg-auto">
            <BButtonToolbar class="mb-2">
                <BPagination class="me-2 mb-0"
                             v-model="currentPage" :disabled="_isLoading" :limit="9"
                             :total-rows="_nbDatasets"
                             :per-page="_pageSize">
                </BPagination>
                <BInputGroup class="me-2" prepend="Page size">
                    <BFormSelect v-model="pageSize" :disabled="_isLoading"
                                 :options="[10, 25, 50, 100]">
                    </BFormSelect>
                </BInputGroup>
                <BInputGroup prepend="Sort by">
                    <BFormSelect v-model="orderBy" :disabled="_isLoading"
                                 :options="orderByFilterChoices">
                    </BFormSelect>
                </BInputGroup>
            </BButtonToolbar>
        </div>

        <BListGroup>
            <DatasetListRow v-for="dataset in _datasets" :key="dataset.id"
                            :dataset="dataset"
                            :selected="_selection.includes(dataset.id)"
                            @select="select" @unselect="unselect">
            </DatasetListRow>
        </BListGroup>

        <div v-if="!_isLoading" class="mt-2">
            Showing {{ _nbDatasetsOnCurrentPage }} digital surface twins out of
            {{ _nbDatasets }}.
        </div>
    </BOverlay>
</template>
