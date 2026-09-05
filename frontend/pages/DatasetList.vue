<script setup lang="ts">

import axios from "axios";

import {computed, onBeforeUnmount, onMounted, ref, watch} from "vue";

import {
    BButton,
    BButtonToolbar,
    BFormGroup,
    BFormSelect,
    BInputGroup,
    BListGroup,
    BOverlay,
    BPagination,
    useToast
} from "bootstrap-vue-next";

import {useDatasetSelectionStore} from "@/stores/datasetSelection";

import SelectionOffcanvas from "@/components/layout/SelectionOffcanvas.vue";
import DatasetListRow from '@/components/manager/DatasetListRow.vue';
import HelpTooltip from '@/components/ui/HelpTooltip.vue';
import SearchTokenInput from '@/components/ui/SearchTokenInput.vue';

const toast = useToast();
const selection = useDatasetSelectionStore();

const props = defineProps({
    apiUrl: {
        type: String,
        default: "/manager/v2/surface/"
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

// Constants; the values are v2 `order` parameters
const orderByFilterChoices = [
    {text: 'Date', value: '-created_at'},
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
// Structured search filters (chips), e.g. [{type: 'author', value: 'Lars'}]
const _searchTokens = ref<any[]>([]);
const _selectionOffcanvasVisible = ref<boolean>(false);
const _sharingStatus = ref(sharingStatusFilterChoices[0].value);

const _datasets = ref([]);
const _nextUrl = ref(null);
const _previousUrl = ref(null);

let searchDelayTimer = null;

// Sequence token to discard stale (out-of-order) responses
let _requestSequence = 0;

// Controller to cancel the in-flight request when a newer one supersedes it
let _abortController: AbortController | null = null;

// Minimum length of the free search text before it is sent to the server
const MIN_SEARCH_LENGTH = 2;

function getDatasets(offset: number = 0) {
    searchDelayTimer = null;
    // Capture the token for this request; responses from superseded requests are ignored.
    const requestId = ++_requestSequence;
    // Cancel any request still in flight; its response would be discarded anyway
    if (_abortController != null) {
        _abortController.abort();
    }
    _abortController = new AbortController();
    _isLoading.value = true;
    _currentPage.value = offset / _pageSize.value + 1;
    let queryUrl = `${props.apiUrl}?offset=${offset}&limit=${_pageSize.value}`;
    queryUrl += `&order=${_orderBy.value}`;
    queryUrl += `&sharing_status=${_sharingStatus.value}`;
    // Collapse published versions of a dataset to the latest one
    queryUrl += `&latest_versions=true`;
    // Structured filters (chips) become dedicated query parameters...
    for (const token of _searchTokens.value) {
        queryUrl += `&${token.type}=${encodeURIComponent(token.value)}`;
    }
    // ...while remaining free text goes through full-text search (only once it
    // is long enough to be meaningful)
    if (_searchTerm.value != null && _searchTerm.value.trim().length >= MIN_SEARCH_LENGTH) {
        queryUrl += `&search=${encodeURIComponent(_searchTerm.value)}`;
    }
    axios.get(queryUrl, {signal: _abortController.signal}).then(response => {
        // Ignore this response if a newer request has been issued in the meantime
        if (requestId !== _requestSequence) {
            return;
        }
        _nbDatasets.value = response.data.count;
        _nbDatasetsOnCurrentPage.value = Math.min(response.data.results.length, _pageSize.value);
        _nextUrl.value = response.data.next;
        _previousUrl.value = response.data.previous;
        _datasets.value = response.data.results;
        _isLoading.value = false;
    }).catch(error => {
        if (requestId !== _requestSequence) {
            return;
        }
        if (axios.isCancel(error)) {
            return;
        }
        toast.create({
            title: "Error fetching datasets",
            body: error,
            variant: 'danger'
        })?.show();
        _isLoading.value = false;
    });
}

onMounted(() => {
    getDatasets();
});

onBeforeUnmount(() => {
    if (searchDelayTimer != null) {
        clearTimeout(searchDelayTimer);
        searchDelayTimer = null;
    }
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

// Re-query (debounced) whenever the free text or the filter chips change
watch([_searchTerm, _searchTokens], () => {
    clearTimeout(searchDelayTimer);
    searchDelayTimer = setTimeout(getDatasets, props.searchDelay);
});

function createSurface() {
    axios.post('/manager/v2/surface/').then(response => {
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
                        description="Search for digital surface twins by name or tags. Type author:, tag: or name: to filter specific fields.">
                <div class="d-flex align-items-center gap-2">
                    <SearchTokenInput v-model:tokens="_searchTokens"
                                      v-model:text="_searchTerm"/>
                    <HelpTooltip label="Tips for searching"
                                 placement="bottom">
                        <p class="mb-1">
                            Searches names, descriptions, tags and authors of
                            datasets and their measurements.
                        </p>
                        <p class="mb-1">
                            <b>Filters:</b> type <code>author:</code>,
                            <code>tag:</code> or <code>name:</code> — the prefix
                            becomes a chip and suggestions appear while you type.
                            Confirm with Enter, remove with &times; or Backspace.
                        </p>
                        <p class="mb-0">
                            <b>Expressions:</b> words combine with AND;
                            <code>OR</code> for alternatives,
                            <code>-word</code> to exclude,
                            <code>"exact phrase"</code> to quote. Example:
                            <code>"AFM surface" imported -material</code>
                        </p>
                    </HelpTooltip>
                </div>
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
    <SelectionOffcanvas
        v-model:visible="_selectionOffcanvasVisible"
    ></SelectionOffcanvas>
</template>
