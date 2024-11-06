<script setup>
import axios from "axios";
import {computed, ref} from 'vue';

import {
    BAlert,
    BButton,
    BButtonGroup,
    BCard,
    BCardBody,
    BFormInput,
    BSpinner,
    useToastController
} from 'bootstrap-vue-next';

const {show} = useToastController();

const properties = defineModel({
    properties: Object,
    default: {}
});

const props = defineProps({
    surfaceUrl: String,
    permission: String
});

function copyProperties() {
    return Object.entries(properties.value).map(([name, property]) => {
        return {name: name, ...property};
    });
}

// this var holds the sate of the editor: view | edit | save
const _isEditing = ref(false);
// count the number of async save jobs
const _nbSaveJobs = ref(0);
// this array holds a backup of the currenty "up to date" properties
// when the state changes this array shall be updated
const _properties = ref(copyProperties());
// this array holds the indexes of the propertie to delet when saved
const _deleted = ref([]);
// this array holds the indexes of the changed properties, no index shall be in edited and deleted
const _edited = ref([]);
//this array hold the indexes of the added properties
const _added = ref([]);

let formIsValid = computed(() => {
    // Property names and values cant be empty
    const emptyFields = _properties.value.some((property) => {
        return property.name === "" || property.value === "";
    })

    //Property names should be uniqe for a digital surface twin
    const hashMap = {}
    const nameDuplicates = _properties.value.some(property => {
        if (hashMap[property.name]) {
            return true
        }
    });
}

// Pull Properties from API and sync table
pullProperties()
    .then(
        syncPropertiesTable
    );

let _isEditing = ref(false);
let _isSaving = ref(false);

function cleanUpAfterSave() {
    // clear deletion list and remove elements
    _deleted.value.sort(function (a, b) {
        return b - a;
    });
    _deleted.value.forEach(index => {
        _properties.value.splice(index, 1);
    });
    _edited.value = [];
    _added.value = [];
    _deleted.value = [];
    _isEditing.value = false;
}

function enterEditMode() {
    if (!_isEditing.value) {
        _isEditing.value = true;
        syncPropertiesTable();
    }
}

function showWarning(msg) {
    show?.({
        props: {
            body: msg,
            variant: "warning"
        }
    });
}

function showError(msg) {
    show?.({
        props: {
            body: msg,
            variant: "danger"
        }
    });
}

const isEditable = computed(() => {
    return ['edit', 'full'].includes(props.permission);
})

function isNumeric(property) {
    return /^-?\d*\.?\d+$/.test(property.value);
}

function addProperty() {
    enterEditMode();
    // Add new empty property if there is no empty last property
    const len = _properties.value.length;
    if (len === 0 || (_properties.value[len - 1].name != '' && _properties.value[len - 1].value != '')) {
        _added.value.push(_properties.value.length);
        _properties.value.push({name: "", value: "", surface: surfaceUrl});
    }
}

function editProperty(index) {
    if (!_edited.value.includes(index) && index < properties.value.length) {
        _edited.value.push(index);
    }
}

function deleteProperty(index) {
    if (index < properties.value.length) {
        _deleted.value.push(index);
    } else { // added property
        // remove prop
        _properties.value.splice(index, 1);
        // remove idx from added list
        _added.value = _added.value.filter((idx) => {
            return idx != index;
        })
        // decrease each index higher than the removed
        _added.value = _added.value.map((idx) => {
            if (idx > index) {
                return idx - 1;
            }
            return idx;
        });
    }
    _edited.value = _edited.value.filter((idx) => {
        return idx != index;
    })

function syncPropertyCreate(index) {
    const property = {..._properties.value[index]};
    _nbSaveJobs.value++;
    axios.post('/manager/api/property/', {
        ...property
    }).then(response => {
        // this is important because the response obj contains the update url!
        _properties.value[index] = response.data
    }).catch(error => {
        _isEditing.value = true;
        showError(`A Error occurred while adding the property '${property.name}' : ${error.response.data.message}`);
        console.log(error);
        _deleted.value.push(index);
    }).finally(() => {
        saveJobFinished();
    });
}

function syncPropertyDelete(index) {
    const property = {..._properties.value[index]};
    _nbSaveJobs.value++;
    axios.delete(property.url).catch(error => {
        _isEditing.value = true;
        showError(`A Error occurred while deleting the property '${property.name}' : ${error.response.data.message}`);
        console.log(error);
        _properties.value[index] = properties.value[property.name];
    }).finally(() => {
        saveJobFinished();
    });

function syncPropertyUpdate(index) {
    const property = {..._properties.value[index]};
    // numeric -> categorical
    if (isNumeric(properties.value[property.name]) && !isNumeric(property)) {
        delete property.unit;
    }
    _nbSaveJobs.value++;
    axios.put(property.url, {
        ...property
    }).catch(error => {
        _isEditing.value = true;
        _properties.value[index] = properties.value[property.name];
        showError(`A Error occurred updating the property '${property.name}': ${error.response.data.message}`);
        console.log(error);
    }).finally(() => {
        saveJobFinished();
    });
}

// view -> edit
function enterEditMode() {
    if (!_isEditing.value) {
        _isEditing.value = true;
        _properties.value = copyProperties();
    }
}

// edit -> view
function discardChanges() {
    _deleted.value = [];
    _edited.value = [];
    _added.value = [];
    // remove added properties
    _properties.value.splice(properties.value.length);
    // restore the others
    for (let index = 0; index < _properties.value.length; index++) {
        _properties.value[index] = properties.value[property.name];
    }
    _isEditing.value = false;
}

function save() {
    // Check for empty names and give warning
    if (_properties.value.filter((property) => property.name === "").length > 0) {
        showWarning("The property name can not be empty");
    }
    // Check for empty values and give warning
    if (_properties.value.filter((property) => property.value === "").length > 0) {
        showWarning("The property value can not be empty");
    }
    // cleanup data
    for (let index = 0; index < _properties.value.length; index++) {
        if (isNumeric(_properties.value[index])) {
            _properties.value[index].value = parseFloat(_properties.value[index].value);
            if (_properties.value[index].unit == null) {
                _properties.value[index].unit = "";
            }
        }
        else {
            propertiesDict[property.name] = {
                value: property.value
            };
        }
    });
    axios.patch(props.surfaceUrl, { properties: propertiesDict }).then((res) => {
        pullProperties()
            .then(
                syncPropertiesTable
            );
        _isEditing.value = false;
        _isSaving.value = false;
    });
}

</script>
<template>
    <b-card>
        <template #header>
            <div class="d-flex">
                <h5 class="flex-grow-1">Properties</h5>
                <b-button size="sm" v-if="!_isEditing && isEditable"
                          @click="enterEditMode"
                          variant="outline-secondary">
                    <i class="fa fa-pen"></i>
                </b-button>
                <b-button-group v-else-if="isEditable" size="sm">
                    <b-button v-if="_isEditing && _nbSaveJobs === 0"
                              @click="discardChanges" variant="danger">
                        Discard
                    </b-button>
                    <b-button :disabled="!formIsValid" @click="save" variant="success">
                        <b-spinner v-if="_isSaving" small />
                        SAVE
                    </b-button>
                </b-button-group>
            </div>
        </template>
        <b-card-body>
            <div v-if="!isEditable && _properties.length == 0">
                This digital surface twin does not have properties.
            </div>
            <div v-else class="border rounded-3 mb-3 p-3">
                <div class="d-flex">
                    <div class="flex-shrink-1 d-flex">
                        <i class="p-2 align-self-center fa-solid fa-hashtag"></i>
                    </div>
                    <div class="w-25 d-flex ms-1 p-2">
                        <span class="fw-bold">
                            Key
                        </span>
                    </div>
                    <div class="w-25 d-flex ms-1 p-2">
                        <span class="fw-bold">
                            Value
                        </span>
                    </div>
                    <div class="d-flex ms-1 p-2">
                        <span class="fw-bold">
                            Unit
                        </span>
                    </div>
                </div>
                <div v-for="(property, index) in _properties" :key="property.name">
                    <div v-if="!_deleted.includes(index)" class="d-flex">
                        <div class="flex-shrink-1 d-flex">
                            <b-button v-if="_isEditing" @click="deleteProperty(index)"
                                      class="m-1 align-self-center" size="sm"
                                      variant="danger" title="remove property">
                                <i class="fa fa-minus"></i>
                            </b-button>
                            <i v-else class="p-2 align-self-center fa fa-bars"></i>
                        </div>
                        <div class="w-25 d-flex ms-1">
                            <b-form-input v-if="_isEditing" @input="editProperty(index)"
                                          size="sm"
                                          placeholder="Property name"
                                          class="align-self-center"
                                          v-model="property.name"></b-form-input>
                            <div v-else class="p-2">
                                <span v-if="property.name === ''" class="fw-lighter">
                                    Property name
                                </span>
                                <span v-else>{{ property.name }}</span>
                            </div>
                        </div>
                        <div class="w-25 d-flex ms-1">
                            <b-form-input v-if="_isEditing" @input="editProperty(index)"
                                          size="sm"
                                          placeholder="Property value"
                                          class="align-self-center"
                                          v-model="property.value"></b-form-input>
                            <div v-else class="p-2">
                                <span v-if="property.value === ''" class="fw-lighter">Property value</span>
                                <span v-else>{{ property.value }}</span>
                            </div>
                        </div>
                        <div v-if="isNumeric(property)" class="d-flex ms-1">
                            <b-form-input v-if="_isEditing" @input="editProperty(index)"
                                          size="sm"
                                          placeholder="dimensionless"
                                          class="align-self-center"
                                          v-model="property.unit"></b-form-input>
                            <div v-else class="p-2">
                                <span v-if="property.unit === ''"
                                      class="fw-lighter"></span>
                                <span v-else>{{ property.unit }}</span>
                            </div>
                        </div>
                        <div v-if="_edited.includes(index) || _added.includes(index)">
                            <i v-if="_isEditing"
                               class="p-2 align-self-center fa fa-upload"></i>
                            <b-spinner v-else-if="_nbSaveJobs > 0" small/>

                        </div>
                    </div>
                </div>
                <div v-if="isEditable" @click="addProperty"
                     class="d-flex highlight-on-hover rounded-3">
                    <div class="p-2 flex-shrink-1">
                        <i class="fa fa-plus"></i>
                    </div>
                    <div class="w-25 p-2">
                        Add property
                    </div>
                </div>
            </div>
        </b-card-body>
    </b-card>
</template>

<style scoped>
.highlight-on-hover {
    border: 1px solid rgba(0, 0, 0, 0);
    transition: background-color 0.3s;
}

.highlight-on-hover:hover {
    border: 1px solid #000000;
    background: var(--bs-secondary-bg-subtle);
    cursor: pointer;
}
</style>
