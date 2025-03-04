<script setup>

import axios from "axios";

import {computed, onMounted, ref} from "vue";

import {
    BButton,
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
    orderBy: String,
    orderByFilterChoices: Object,
    pageSize: Number,
    sharingStatus: String,
    sharingStatusFilterChoices: Object,
    searchTerm: String
});


// UI logic
const _currentPage = ref(props.currentPage);
const _isLoading = ref(props.isLoading);
const _nbDatasets = ref(null);
const _nbDatasetsOnCurrentPage = ref(null);
const _orderBy = ref(props.orderBy);
const _pageSize = ref(props.pageSize);
const _searchTerm = ref(props.searchTerm);
const _selection = ref(props.initialSelection);
const _sharingStatus = ref(props.sharingStatus);

const _datasets = ref([]);
const _nextUrl = ref(null);
const _previousUrl = ref(null);

function getDatasets(offset = 0) {
    _isLoading.value = true;
    _currentPage.value = offset / _pageSize.value;
    axios.get(`${props.apiUrl}?offset=${offset}&limit=${_pageSize.value}`).then(response => {
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
        <div class="row row-cols-lg-auto mb-2">
            <div v-if="_searchTerm" class="form-group">
                <button class="btn btn-warning form-control" type="button"
                        id="clear-search-term-btn"
                        @click="clearSearchTerm" :disabled="_isLoading">
                    Clear filter for <b>{{ _searchTerm }}</b>
                </button>
            </div>
            <div v-else class="form-group">
                <button class="btn btn-outline-info form-control disabled"
                        type="button">
                    Not filtered for search term
                </button>
            </div>

            <BFormGroup>
                <BFormSelect name="sharing_status" class="form-control"
                             v-model="_sharingStatus" @change="getDatasets"
                             :disabled="_isLoading"
                             :options="sharingStatusFilterChoices">
                </BFormSelect>
            </BFormGroup>

            <div class="col-md-4">
                <div v-if="isAnonymous" class="form-group">
                    <BButton variant="primary"
                             title="Please sign-in to use this feature"
                             disabled>
                        Create new digital surface twin
                    </BButton>
                </div>
                <div v-if="!isAnonymous" class="form-group"
                     title="Create a new digital surface twin">
                    <BButton variant="primary" class="form-control"
                             @click="createSurface"
                             :disabled="_isLoading">
                        Create new digital surface twin
                    </BButton>
                </div>
            </div>
        </div>
        <div class="row row-cols-lg-auto">
            <div class="col-md-4">
                <BPagination v-model="currentPage" :disabled="_isLoading" :limit="9"
                             :total-rows="_nbDatasets"
                             :per-page="_pageSize">
                </BPagination>
            </div>
            <div class="col-md-4">
                <BInputGroup prepend="Page size">
                    <BFormSelect v-model="pageSize" :disabled="_isLoading"
                                 :options="[10, 25, 50, 100]">
                    </BFormSelect>
                </BInputGroup>
            </div>
            <div class="col-md-4">
                <BInputGroup prepend="Sort by">
                    <BFormSelect v-model="orderBy" :disabled="_isLoading"
                                 :options="orderByFilterChoices">
                    </BFormSelect>
                </BInputGroup>
            </div>
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
