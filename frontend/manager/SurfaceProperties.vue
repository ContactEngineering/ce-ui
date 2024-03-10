<script setup>

import axios from "axios";
import {ref, computed} from 'vue';

import {BCard, BCardBody, BButton, BButtonGroup, BSpinner, BFormInput, BAlert} from 'bootstrap-vue-next';


const props = defineProps({
    surfaceUrl: String,
    properties: Array,
    permission: String
});


function copyProperties() {
    return props.properties.map(property => {
        return {...property}
    });
}


// this var holds the sate of the editor: view | edit | save
let _isEditing = ref(false);
// count the number of async save jobs
let _nbSaveJobs = ref(0);
// this array holds a backup of the currenty "up to date" properties
// when the state changes this array shall be updated
let _backupProperties = copyProperties();
// this array holds the indexes of the propertie to delet when saved
let _deleted = ref([]);
// this array holds the indexes of the changed properties, no index shall be in edited and deleted
let _edited = ref([]);
//this array hold the indexes of the added properties
let _added = ref([]);

let _messages = ref([]);

let formIsValid = computed(() => {
    return props.properties.every((property) => {
        return property.name != "" && property.value != "";
    })
});

function cleanUpAfterSave() {
    // clear deletion list and remove elements
    _deleted.value.sort(function (a, b) {
        return b - a;
    });
    _deleted.value.forEach(index => {
        props.properties.splice(index, 1);
    });
    _edited.value = [];
    _added.value = [];
    _deleted.value = [];
    _isEditing.value = false;
}

function saveJobFinished() {
    _nbSaveJobs.value--;
    if (_nbSaveJobs.value === 0) {
        cleanUpAfterSave();
    }
}

function showWarning(msg) {
    _messages.value.push({type: 'warning', visible: true, content: msg});
}

function showError(msg) {
    _messages.value.push({type: 'danger', visible: true, content: msg});
}

const isEditable = computed(() => {
    return ['edit', 'full'].includes(props.permission);
})

function isNumeric(property) {
    return /^-?\d*\.?\d+$/.test(property.value);
}

function addProperty() {
    // Enter state === 'edit'
    enterEditMode();
    // Add new empty property if there is no empty last property
    const len = props.properties.length;
    if (len === 0 || (props.properties[len - 1].name != '' && props.properties[len - 1].value != '')) {
        _added.value.push(props.properties.length);
        props.properties.push({name: "", value: "", surface: surfaceUrl});
    }
}

function editProperty(index) {
    if (!_edited.value.includes(index) && index < _backupProperties.length) {
        _edited.value.push(index);
    }
}

function deleteProperty(index) {
    if (index < _backupProperties.length) {
        _deleted.value.push(index);
    } else { // added property
        // remove prop
        props.properties.splice(index, 1);
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
}

function syncPropertyCreate(index) {
    const property = {...props.properties[index]};
    _nbSaveJobs.value++;
    axios.post('/manager/api/property/', {
        ...property
    }).then(response => {
        // this is important because the response obj contains the update url!
        props.properties[index] = response.data
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
    const property = {...props.properties[index]};
    _nbSaveJobs.value++;
    axios.delete(property.url).catch(error => {
        _isEditing.value = true;
        showError(`A Error occurred while deleting the property '${property.name}' : ${error.response.data.message}`);
        console.log(error);
        props.properties[index] = _backupProperties[index];
    }).finally(() => {
        saveJobFinished();
    });
}

function syncPropertyUpdate(index) {
    const property = {...props.properties[index]};
    // numeric -> categorical
    if (isNumeric(_backupProperties[index]) && !isNumeric(property)) {
        delete property.unit;
    }
    _nbSaveJobs.value++;
    axios.put(property.url, {
        ...property
    }).catch(error => {
        _isEditing.value = true;
        props.properties[index] = _backupProperties[index];
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
        _backupProperties = copyProperties();
    }
}

// edit -> view
function discardChanges() {
    _deleted.value = [];
    _edited.value = [];
    _added.value = [];
    // remove added properties
    props.properties.splice(_backupProperties.length);
    // restore the others
    for (let index = 0; index < props.properties.length; index++) {
        props.properties[index] = _backupProperties[index];
    }
    _isEditing.value = false;
}

// edit -> save -> edit | view
function save() {
    // Check for empty names and give warning
    if (props.properties.filter((property) => property.name === "").length > 0) {
        showWarning("The property name can not be empty");
    }
    // Check for empty values and give warning
    if (props.properties.filter((property) => property.value === "").length > 0) {
        showWarning("The property value can not be empty");
    }
    // cleanup data
    for (let index = 0; index < props.properties.length; index++) {
        if (isNumeric(props.properties[index])) {
            props.properties[index].value = parseFloat(props.properties[index].value);
            if (props.properties[index].unit == null) {
                props.properties[index].unit = "";
            }
        }
    }

    _isEditing.value = false;
    _edited.value.forEach(syncPropertyUpdate);
    _deleted.value.forEach(syncPropertyDelete);
    _added.value.forEach(syncPropertyCreate);
}
</script>

<template>
    <b-card>
        <template #header>
            <div class="d-flex">
                <h5 class="flex-grow-1">Properties</h5>
                <b-button size="sm" v-if="!_isEditing && isEditable" @click="enterEditMode"
                          variant="outline-secondary">
                    <i class="fa fa-pen"></i>
                </b-button>
                <b-button-group v-else-if="isEditable" size="sm">
                    <b-button v-if="_isEditing && _nbSaveJobs === 0" @click="discardChanges" variant="danger">
                        Discard
                    </b-button>
                    <b-button :disabled="!formIsValid" @click="save" variant="success">
                        <b-spinner v-if="_nbSaveJobs > 0" small/>
                        SAVE
                    </b-button>
                </b-button-group>
            </div>
        </template>
        <b-card-body>
            <div v-if="!isEditable && props.properties.length == 0">
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
                <div v-for="(property, index) in props.properties" :key="property.url">
                    <div v-if="!_deleted.includes(index)" class="d-flex">
                        <div class="flex-shrink-1 d-flex">
                            <b-button v-if="_isEditing" @click="deleteProperty(index)"
                                      class="m-1 align-self-center" size="sm" variant="danger" title="remove property">
                                <i class="fa fa-minus"></i>
                            </b-button>
                            <i v-else class="p-2 align-self-center fa fa-bars"></i>
                        </div>
                        <div class="w-25 d-flex ms-1">
                            <b-form-input v-if="_isEditing" @input="editProperty(index)" size="sm"
                                          placeholder="Property name" class="align-self-center"
                                          v-model="property.name"></b-form-input>
                            <div v-else class="p-2">
                                <span v-if="property.name === ''" class="fw-lighter">
                                    Property name
                                </span>
                                <span v-else>{{ property.name }}</span>
                            </div>
                        </div>
                        <div class="w-25 d-flex ms-1">
                            <b-form-input v-if="_isEditing" @input="editProperty(index)" size="sm"
                                          placeholder="Property value" class="align-self-center"
                                          v-model="property.value"></b-form-input>
                            <div v-else class="p-2">
                                <span v-if="property.value === ''" class="fw-lighter">Property value</span>
                                <span v-else>{{ property.value }}</span>
                            </div>
                        </div>
                        <div v-if="isNumeric(property)" class="d-flex ms-1">
                            <b-form-input v-if="_isEditing" @input="editProperty(index)" size="sm"
                                          placeholder="dimensionless" class="align-self-center"
                                          v-model="property.unit"></b-form-input>
                            <div v-else class="p-2">
                                <span v-if="property.unit === ''" class="fw-lighter"></span>
                                <span v-else>{{ property.unit }}</span>
                            </div>
                        </div>
                        <div v-if="_edited.includes(index) || _added.includes(index)">
                            <i v-if="_isEditing" class="p-2 align-self-center fa fa-upload"></i>
                            <b-spinner v-else-if="_nbSaveJobs > 0" small/>
                        </div>
                    </div>
                </div>
                <div v-if="isEditable" @click="addProperty" class="d-flex highlight-on-hover rounded-3">
                    <div class="p-2 flex-shrink-1">
                        <i class="fa fa-plus"></i>
                    </div>
                    <div class="w-25 p-2">
                        Add property
                    </div>
                </div>
            </div>
            <div v-for="message in _messages">
                <b-alert v-model="message.visible" dismissible :variant="message.type">
                    {{ message.content }}
                </b-alert>
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
