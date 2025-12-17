<script setup lang="ts">

import { computed, onMounted, ref } from "vue";

import {
    QBtn,
    QBtnDropdown,
    QIcon,
    QInput,
    QInfiniteScroll,
    QList,
    QItem,
    QItemSection,
    QItemLabel,
    QDialog,
    QCard,
    QCardSection,
    QCardActions,
    QSpinner,
    QMarkupTable,
    ClosePopup
} from "quasar";

const vClosePopup = ClosePopup;

import { useNotify } from "@/utils/notify";
import { managerApiSurfaceList, managerApiSurfaceCreate } from "@/api";

import { useDatasetSelectionStore } from "../stores/datasetSelection";

import DatasetListRow from '../manager/DatasetListRow.vue';
import SelectionOffcanvas from "../base/SelectionOffcanvas.vue";

const { show } = useNotify();
const selection = useDatasetSelectionStore();

const props = defineProps({
    isAnonymous: Boolean,
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
const BATCH_SIZE = 20;

const orderByFilterChoices = [
    { label: 'Date', value: 'date' },
    { label: 'Name', value: 'name' },
];
const sharingStatusFilterChoices = [
    { label: 'All accessible', value: 'all' },
    { label: 'Created by me', value: 'own' },
    { label: 'Shared with me', value: 'others' },
    { label: 'Published', value: 'published' }
];

// UI logic
const _isLoading = ref<boolean>(false);
const _nbDatasets = ref<number>(null);
const _orderBy = ref(orderByFilterChoices[0].value);
const _searchTerm = ref<string>(props.searchTerm);
const _searchInfoModalVisible = ref<boolean>(false);
const _selectionOffcanvasVisible = ref<boolean>(false);
const _sharingStatus = ref(sharingStatusFilterChoices[0].value);

const _datasets = ref([]);
const _hasMore = ref(true);
const _infiniteScrollRef = ref(null);

let searchDelayTimer = null;

async function loadMore(index: number, done: (stop?: boolean) => void) {
    try {
        const response = await managerApiSurfaceList({
            query: {
                offset: _datasets.value.length,
                limit: BATCH_SIZE,
                order_by: _orderBy.value,
                sharing_status: _sharingStatus.value,
                search: _searchTerm.value || undefined
            } as any
        });

        _nbDatasets.value = response.data.count;
        _datasets.value = [..._datasets.value, ...response.data.results];
        _hasMore.value = response.data.next !== null;

        done(!_hasMore.value);
    } catch (error) {
        show?.({
            props: {
                title: "Error fetching datasets",
                body: error,
                variant: 'danger'
            }
        });
        done(true);
    }
}

function resetAndReload() {
    _datasets.value = [];
    _hasMore.value = true;
    _nbDatasets.value = null;
    // Trigger infinite scroll to load first batch
    _infiniteScrollRef.value?.resume();
    _infiniteScrollRef.value?.trigger();
}

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
        searchDelayTimer = setTimeout(resetAndReload, props.searchDelay);
    }
});

function orderByChanged(value: string) {
    _orderBy.value = value;
    resetAndReload();
}

function sharingStatusChanged(value: string) {
    _sharingStatus.value = value;
    resetAndReload();
}

async function createSurface() {
    const response = await managerApiSurfaceCreate();
    window.location.href = `/ui/dataset-detail/${response.data.id}/`;
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
                    <QIcon name="search" />
                </template>
                <template v-slot:append>
                    <QBtn flat round dense icon="info" size="sm" @click="_searchInfoModalVisible = true" />
                </template>
            </QInput>
        </div>
        <div>
            <QBtnDropdown flat dense
                          :label="sharingStatusFilterChoices.find(o => o.value === _sharingStatus)?.label"
                          icon="filter_list">
                <QList>
                    <QItem v-for="option in sharingStatusFilterChoices"
                           :key="option.value"
                           clickable
                           v-close-popup
                           :active="_sharingStatus === option.value"
                           @click="sharingStatusChanged(option.value)">
                        <QItemSection>
                            <QItemLabel>{{ option.label }}</QItemLabel>
                        </QItemSection>
                    </QItem>
                </QList>
            </QBtnDropdown>
        </div>
        <div>
            <QBtnDropdown flat dense
                          :label="`Sort: ${orderByFilterChoices.find(o => o.value === _orderBy)?.label}`"
                          icon="sort">
                <QList>
                    <QItem v-for="option in orderByFilterChoices"
                           :key="option.value"
                           clickable
                           v-close-popup
                           :active="_orderBy === option.value"
                           @click="orderByChanged(option.value)">
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
                  icon="add"
                  label="New"
                  @click="createSurface" />
        </div>
    </div>

    <div class="row items-center q-mb-sm">
        <div class="text-caption text-grey-7">
            <span v-if="_nbDatasets !== null">{{ _nbDatasets }} digital surface twins</span>
        </div>
        <div class="col-grow" />
        <QBtn v-if="selection.nbSelected === 0"
              flat dense
              disable
              icon="check_box_outline_blank"
              :label="`${selection.nbSelected} selected`" />
        <QBtn v-if="selection.nbSelected > 0"
              flat dense
              color="warning"
              icon="check_box"
              :label="`${selection.nbSelected} selected`"
              @click="_selectionOffcanvasVisible = true" />
    </div>

    <QInfiniteScroll ref="_infiniteScrollRef" @load="loadMore" :offset="250">
        <QList bordered separator class="rounded-borders">
            <DatasetListRow v-for="dataset in _datasets"
                            :key="dataset.id"
                            :dataset="dataset"
                            v-model:selected="selection.datasetIds" />
        </QList>

        <template v-slot:loading>
            <div class="row justify-center q-my-md">
                <QSpinner color="primary" size="2em" />
            </div>
        </template>
    </QInfiniteScroll>

    <div v-if="_datasets.length > 0 && !_hasMore" class="text-center text-caption text-grey-6 q-mt-md">
        End of list
    </div>

    <div v-if="_datasets.length === 0 && !_hasMore" class="text-center q-pa-xl">
        <QIcon name="search_off" size="3rem" color="grey-5" />
        <div class="text-h6 text-grey-7 q-mt-md">No datasets found</div>
        <div class="text-caption text-grey-6">Try adjusting your search or filters</div>
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
