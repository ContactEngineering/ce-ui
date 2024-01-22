<script setup>
/**
 * Compoment which represents the search result tree in the select page.
 * The tree is either in "surface list" mode or "tag tree" mode.
 *
 * "surface list" mode: Shows list of surfaces and their topographies underneath
 * "tag tree" mode: Shows tree of tags (multiple levels) and underneath the surfaces
 *                  and topographies tagged with the corresponding tags
 *
 * @type {Vue}
 *
 * See https://vuejs.org/v2/examples/select2.html as example how to wrap 3rd party code into a component
 */

import $ from 'jquery';
import axios from "axios";

import {computed, onMounted, ref} from "vue";

import {BFormSelect, BInputGroup, BPagination, BSpinner} from "bootstrap-vue-next";

import {createTree} from 'jquery.fancytree';

import 'jquery.fancytree/dist/modules/jquery.fancytree.glyph';
import 'jquery.fancytree/dist/modules/jquery.fancytree.table';

import Basket from './Basket.vue';

const props = defineProps({
    baseUrls: Object,
    category: String,
    categoryFilterChoices: Object,
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
    searchTerm: String,
    treeMode: String
});


// UI logic
const _category = ref(props.category);
const _currentPage = ref(props.currentPage);
const _isLoading = ref(props.isLoading);
const _numItems = ref(null);
const _numItemsOnCurrentPage = ref(null);
const _numPages = ref(null);
const _orderBy = ref(props.orderBy);
const _pageRange = ref(null);
const _pageSize = ref(props.pageSize);
const _pageUrls = ref(null);
const _searchTerm = ref(props.searchTerm);
const _selection = ref(props.initialSelection);
const _sharingStatus = ref(props.sharingStatus);
const _treeMode = ref(props.treeMode);

// The actual fancy tree
const _tree = ref(null);

// Constants
const _treeModeInfos = {
    "surface list": {
        element_kind: "digital surface twins",
        hint: 'Analyze selected items by clicking on the "Analyze" button.',
    },
    "tag tree": {
        element_kind: "top level tags",
        hint: "Tags can be introduced or changed when editing meta data of surfaces and topographies.",
    }
};

onMounted(() => {
    console.log(props.orderBy);

    // init fancytree
    _tree.value = createTree('#surface-tree', {
            extensions: ["glyph", "table"],
            glyph: {
                preset: "awesome5",
                map: {
                    // Override distinct default icons here
                    folder: "fa-folder",
                    folderOpen: "fa-folder-open"
                }
            },
            types: {
                "surface": {icon: "far fa-gem", iconTooltip: "This is a digital surface twin"},
                "topography": {icon: "far fa-file", iconTooltip: "This is a measurement"},
                "tag": {icon: "fas fa-tag", iconTooltip: "This is a tag"},
            },
            icon(event, data) {
                // data.typeInfo contains tree.types[node.type] (or {} if not found)
                // Here we will return the specific icon for that type, or `undefined` if
                // not type info is defined (in this case a default icon is displayed).
                return data.typeInfo.icon;
            },
            iconTooltip(event, data) {
                return data.typeInfo.iconTooltip; // set tooltip which appears when hovering an icon
            },
            table: {
                checkboxColumnIdx: null,    // render the checkboxes into the this column index (default: nodeColumnIdx)
                indentation: 20,            // indent every node level by these number of pixels
                nodeColumnIdx: 0            // render node expander, icon, and title to this column (default: #0)
            },
            autoActivate: true,
            titlesTabbable: false,
            tabindex: -1,
            focusOnSelect: false,
            scrollParent: window,
            autoScroll: true,
            scrollOfs: {top: 200, bottom: 50},
            checkbox: true,
            selectMode: 2, // 'multi'
            source: {
                url: searchUrl.value.toString(),  // this is a computed property, see below
                cache: false
            },
            postProcess(event, data) {
                console.log("PostProcess: ", data);
                _numPages.value = data.response.num_pages;
                _numItems.value = data.response.num_items;
                _currentPage.value = data.response.current_page;
                _numItemsOnCurrentPage.value = data.response.num_items_on_currentPage;
                _pageRange.value = data.response.page_range;
                _pageUrls.value = data.response.page_urls;
                _pageSize.value = data.response.page_size;
                // assuming the Ajax response contains a list of child nodes:
                // We replace the result
                data.result = data.response.page_results;
                _isLoading.value = false;
            },
            select(event, data) {
                const node = data.node;
                const is_selected = node.isSelected();
                if (node.data.urls !== undefined) {
                    if (is_selected) {
                        axios.post(node.data.urls.select)
                            .then(response => {
                                _selection.value = response.data;
                                setSelectedByKey(node.key, true);
                            })
                            .catch(error => {
                                console.error("Could not select: " + error);
                            });
                    } else {
                        axios.post(node.data.urls.unselect)
                            .then(response => {
                                _selection.value = response.data;
                                setSelectedByKey(node.key, false);
                            })
                            .catch(error => {
                                console.error("Could not unselect: " + error);
                            });
                    }
                } else {
                    console.log("No urls defined for node. Cannot pass selection to session.");
                }
            },
            renderTitle(event, data) {
                return " ";
            },
            renderColumns(event, data) {
                const node = data.node;
                const $tdList = $(node.tr).find(">td");

                /**
                 Add special css classes to nodes depending on type
                 */

                let extra_classes = {
                    surface: [],
                    topography: [],
                    tag: ['font-italic']
                };

                node.addClass('select-tree-item')

                extra_classes[node.type].forEach(function (c) {
                    node.addClass(c);
                });

                let description_html = "";
                // DOI badge added here
                if (node.data.publication_doi) {
                    description_html += `<a class="badge bg-dark me-1 text-decoration-none" href="https://doi.org/${node.data.publication_doi}">${node.data.publication_doi}</a>`;
                }
                // License image
                if (node.data.publication_license) {
                    description_html += `<img src="/static/images/cc/${node.data.publication_license}.svg" title="Dataset can be reused under the terms of a Creative Commons license." style="float:right">`;
                }

                // Tags
                if (node.data.category) {
                    description_html += `<p class='badge bg-light text-dark me-1'>${node.data.category_name}</p>`;
                }

                if (node.data.sharing_status == "own") {
                    description_html += `<p class='badge bg-info me-1'>Created by you</p>`;
                } else if (node.data.sharing_status == "shared") {
                    description_html += `<p class='badge bg-info me-1'>Shared by ${node.data.creator_name}</p>`;
                }

                if (node.data.tags !== undefined) {
                    node.data.tags.forEach(function (tag) {
                        description_html += "<p class='badge bg-success me-1'>" + tag + "</p>";
                    });
                }

                // Title
                description_html += `<p class="select-tree-title">${node.data.name}</p>`;

                let publication_info = "";
                if (node.data.publication_authors) {
                    const date = new Date(node.data.publication_date);
                    publication_info += `${node.data.publication_authors} (published ${date.toISOString().substring(0, 10)})`;
                } else {
                    if (node.type == "surface") {
                        publication_info += `This dataset is unpublished. It was created by ${node.data.creator_name}`;
                        if (node.data.creation_datetime) {
                            const date = new Date(node.data.creation_datetime);
                            publication_info += ` on ${date.toISOString().substring(0, 10)}`;
                        }
                        publication_info += ".";
                    }
                }

                if (publication_info) {
                    description_html += `<p class="select-tree-authors">${publication_info}</p>`;
                }

                // Set column with description
                if (node.data.description !== undefined) {
                    description_html += `<p class='select-tree-description'>${node.data.description}</p>`;
                }

                let info_footer = "";
                if (node.data.topography_count && node.data.version) {
                    info_footer += `This is version ${node.data.version} of this digital surface twin and contains ${node.data.topography_count} measurements.`
                } else if (node.data.version) {
                    info_footer += `This is version ${node.data.version} of this dig77ital surface twin.`
                } else if (node.data.topography_count) {
                    info_footer += `This digital surface twin contains ${node.data.topography_count} measurements.`
                }
                if ((node.type == "topography") && (node.data.sharing_status != "published")) {
                    info_footer += `Uploaded by ${node.data.creator_name}.`;
                }
                if (info_footer) {
                    description_html += `<p class="select-tree-info">${info_footer}</p>`
                }

                $tdList
                    .eq(1)
                    .html(description_html);

                // Set columns with buttons:
                if (node.type !== "tag") {
                    const actions_html = `
                            <div class="btn-group-vertical btn-group-sm" role="group" aria-label="Actions">
                             ${item_buttons(node.data.urls)}
                            </div>
                          `;
                    $tdList
                        .eq(2)
                        .html(actions_html);
                }
            },
        }
    ); // fancytree()
    _isLoading.value = true;
});

const currentPage = computed({
    get() {
        return _currentPage.value;
    },
    set(value) {
        _currentPage.value = value;

        if ((value >= 1) && (value <= _pageRange.value.length)) {
            const pageUrl = new URL(_pageUrls.value[value - 1]);

            console.log("Loading page " + value + " from " + pageUrl + "..");
            _tree.value.setOption('source', {
                url: pageUrl,
                cache: false,
            });
            _isLoading.value = true;
        } else {
            console.warn("Cannot load page " + value + ", because the page number is invalid.")
        }
    }
});

const orderBy = computed({
    get() {
        return _orderBy.value;
    },
    set(value) {
        _orderBy.value = value;
        reload();
    }
});

const pageSize = computed({
    get() {
        return _pageSize.value;
    },
    set(value) {
        _pageSize.value = value;
        reload();
    }
});

const searchUrl = computed(() => {
    // Returns URL object

    let url = new URL(props.baseUrls[_treeMode.value]);

    // replace page_size parameter
    // ref: https://usefulangle.com/post/81/javascript-change-url-parameters
    let queryParams = url.searchParams;

    queryParams.set("search", _searchTerm.value);  // empty string -> no search
    queryParams.set("category", _category.value);
    queryParams.set("order_by", _orderBy.value);
    queryParams.set("sharing_status", _sharingStatus.value);
    queryParams.set('page_size', _pageSize.value);
    queryParams.set('page', currentPage.value);
    queryParams.set('tree_mode', _treeMode.value);
    url.search = queryParams.toString();
    // url = url.toString();

    console.log("Requested search URL: " + url.toString());

    return url;
});

function clearSearchTerm() {
    console.log("Clearing search term...");
    _searchTerm.value = '';
    reload();
}

function reload() {
    /* Reload means: the tree must be completely reloaded,
       with currently set state of the select tab,
       except of the page number which should be 1. */
    _currentPage.value = 1;

    _tree.value.setOption('source', {
        url: searchUrl.value.toString(),
        cache: false,
    });
    _isLoading.value = true;
}

function setSelectedByKey(key, selected) {
    // Set selection on all nodes with given key and
    // set it to "selected" (bool)
    _tree.value.findAll(function (node) {
        return node.key == key;
    }).forEach(function (node) {
        node.setSelected(selected, {noEvents: true});
        // we only want to set the checkbox here, we don't want to simulate the click
    })
}

function setSelectedKeys(keys) {
    // Select on all nodes with key in `keys`
    console.log(_tree.value);
    _tree.value.visit(function (node) {
        node.setSelected(keys.includes(node.key), {noEvents: true});
    })
}

function unselect(basket, keys) {
    setSelectedKeys(keys);
}

function createSurface() {
    axios.post('/manager/api/surface/').then(response => {
        window.location.href = `/ui/html/surface/?surface=${response.data.id}`;
    });
}
</script>

<template>
    <basket :basket-items="_selection"
            @unselect-successful="unselect">
    </basket>
    <div class="row row-cols-lg-auto mb-2">
        <div v-if="_searchTerm" class="form-group">
            <button class="btn btn-warning form-control" type="button"
                    id="clear-search-term-btn"
                    @click="clearSearchTerm"
                    :disabled="_isLoading">
                Clear filter for <b>{{ _searchTerm }}</b>
            </button>
        </div>
        <div v-else class="form-group">
            <button class="btn btn-outline-info form-control disabled" type="button">
                Not filtered for search term
            </button>
        </div>

        <div class="form-group">
            <select name="category"
                    class="form-control"
                    v-model="_category"
                    @change="reload"
                    :disabled="_isLoading">
                <option v-for="(choiceLabel, choiceVal) in categoryFilterChoices"
                        v-bind:value="choiceVal" v-bind:selected="choiceVal==_category">
                    {{ choiceLabel }}
                </option>
            </select>
        </div>

        <div class="form-group">
            <select name="sharing_status"
                    class="form-control"
                    v-model="_sharingStatus"
                    @change="reload"
                    :disabled="_isLoading">
                <option v-for="(choiceLabel, choiceVal) in sharingStatusFilterChoices"
                        v-bind:value="choiceVal" v-bind:selected="choiceVal==_sharingStatus">
                    {{ choiceLabel }}
                </option>
            </select>
        </div>

        <div class="col-md-4">
            <div v-if="isAnonymous" class="form-group">
                <button class="btn btn-primary form-control disabled"
                        title="Please sign-in to use this feature"
                        disabled>
                    Create new digital surface twin
                </button>
            </div>
            <div v-if="!isAnonymous" class="form-group" title="Create a new digital surface twin">
                <button class="btn btn-primary form-control"
                        @click="createSurface"
                        :disabled="_isLoading">
                    Create new digital surface twin
                </button>
            </div>
        </div>
    </div>
    <div class="row row-cols-lg-auto">
        <div class="col-md-4">
            <div id="tree-selector" class="btn-group">
                <label v-for="choice in
                     [ { label: 'Surface list',
                         value: 'surface list',
                         icon_class: 'far fa-gem'},
                       { label:'Tag tree',
                         value: 'tag tree',
                         icon_class: 'fas fa-tag'}]"
                       v-bind:class="{active: _treeMode==choice.value,
                                      'btn': true,
                                      'btn-success': _treeMode==choice.value,
                                      'btn-outline-success': _treeMode!=choice.value,
                                      'disabled': _isLoading}">
                    <input type="radio"
                           class="btn-check"
                           autocomplete="off"
                           name="tree_mode"
                           v-bind:value="choice.value"
                           v-model="_treeMode"
                           @change="reload">
                    <span><i v-bind:class="choice.icon_class"></i> {{ choice.label }}</span>
                </label>
            </div>
        </div>
        <div class="col-md-4">
            <b-pagination v-model="currentPage"
                          :disabled="_isLoading"
                          :limit="9"
                          :total-rows="_numItems"
                          :per-page="_pageSize">
            </b-pagination>
        </div>
        <div class="col-md-4">
            <b-input-group prepend="Page size">
                <b-form-select v-model="pageSize"
                               :disabled="_isLoading"
                               :options="[10, 25, 50, 100]">
                </b-form-select>
            </b-input-group>
        </div>
        <div class="col-md-4">
            <b-input-group prepend="Sort by">
                <b-form-select v-model="orderBy"
                               :disabled="_isLoading"
                               :options="orderByFilterChoices">
                </b-form-select>
            </b-input-group>
        </div>
    </div>

    <div v-if="_isLoading"
         class="d-flex justify-content-center mt-5">
        <div class="flex-column text-center">
            <b-spinner/>
            <p>Loading...</p>
        </div>
    </div>

    <div id="scrollParent">
        <table id="surface-tree" class="table table-condensed surface-tree">
            <colgroup>
                <col width="150rem">
                <col>
                <col width="100rem">
            </colgroup>
            <thead>
            <tr>
                <th scope="col">Select</th>
                <th scope="col">Description</th>
                <th scope="col">Actions</th>
            </tr>
            </thead>
            <tbody>
            </tbody>
        </table>
    </div>
    <div>
    <span v-if="!_isLoading">
      Showing {{ _numItemsOnCurrentPage }} {{ _treeModeInfos[_treeMode].element_kind }} out of {{ _numItems }}.
      {{ _treeModeInfos[_treeMode].hint }}
    </span>
    </div>
</template>
