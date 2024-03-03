<script setup>
import { BCard, BCardBody, BButton, BButtonGroup, BSpinner, BFormInput, BAlert } from 'bootstrap-vue-next';
import { ref, computed } from 'vue';
import axios from "axios";
import cloneDeep from 'lodash/cloneDeep';


const props = defineProps({
    surfaceUrl: String,
    properties: Array,
    permission: String
});


const copyProperties = () => {
    return props.properties.map(property => {
        return { ...property }
    });
}


// this var holds the sate of the editor: view | edit | save
let state = ref('view');
// this array holds a backup of the currenty "up to date" properties
// when the state changes this array shall be updated
let backup_properties = copyProperties();
// this array holds the indexes of the propertie to delet when saved
let deleted = ref([]);
// this array holds the indexes of the changed properties, no index shall be in edited and deleted
let edited = ref([]);
//this array hold the indexes of the added properties
let added = ref([]);

let messages = ref([]);

let formIsValid = computed(() => {
    return props.properties.every((property) => {
        return property.name != "" && property.value != "";
    })
});

const showWarning = (msg) => {
    messages.value.push({ type: 'warning', visible: true, content: msg });
}

const showError = (msg) => {
    messages.value.push({ type: 'danger', visible: true, content: msg });
}

const isEditable = computed(() => {
    return ['edit', 'full'].includes(props.permission);
})

function isNumeric(property) {
    return /^-?\d*\.?\d+$/.test(property.value);
}

const addProperty = () => {
    // Enter state === 'edit'
    if (!(state.value === 'edit')) {
        enterEditMode();
    }
    // Add new empty property if there is no empty last property
    const len = props.properties.length;
    if (len === 0 || (props.properties[len - 1].name != '' && props.properties[len - 1].value != '')) {
        added.value.push(props.properties.length);
        props.properties.push({ name: "", value: "", surface: surfaceUrl});
    }
}

const editProperty = (index) => {
    if (!edited.value.includes(index) && index < backup_properties.length) {
        edited.value.push(index);
    }
}

const deleteProperty = (index) => {
    if (index < backup_properties.length) {
        deleted.value.push(index);
    }else {
        props.properties.splice(index, 1);
        added.value = added.value.filter((idx) => {
            return idx != index;
        })
    }
    edited.value = edited.value.filter((idx) => {
        return idx != index;
    })
}

const syncPropertyCreate = (index) => {
    const property = {...props.properties[index]};
    axios.post('/manager/api/property/', {...property}).catch(error => {
        showError(`A Error occurred: ${error.message}`);
        console.log(error);
        props.properties.splice(index, 1);
    }).finally(() => {
        added.value = added.value.filter((idx) => {
            return idx != index;
        })
    });
}

const syncPropertyDelete = (index) => {
    const property = {...props.properties[index]};
    axios.delete(property.url).catch(error => {
        showError(`A Error occurred: ${error.message}`);
        console.log(error);
        props.properties[index] = backup_properties[index];
    }).finally(() => {
        deleted.value = deleted.value.filter((idx) => {
            return idx != index;
        })
    });
}
const syncPropertyUpdate = (index) => {
    const property = {...props.properties[index]};
    // numeric -> categorical
    if (isNumeric(backup_properties[index]) && !isNumeric(property)){
        delete property.unit;
    }
    axios.put(property.url, {
        ...property
    }).catch(error => {
        props.properties[index] = backup_properties[index];
        showError(`A Error occurred: ${error.message}`);
        console.log(error);
    }).finally(() => {
        edited.value = edited.value.filter((idx) => {
            return idx != index;
        })
    });
}

// view -> edit
const enterEditMode = () => {
    state.value = 'edit';
    backup_properties = copyProperties();
}

// edit -> view
const discardChanges = () => {
    deleted.value = [];
    edited.value = [];
    props.properties.splice(backup_properties.length);
    for (let index = 0; index < props.properties.length; index++) {
        props.properties[index] = backup_properties[index];
    }
    state.value = 'view';
}

// edit -> save -> edit | view
const save = () => {
    state.value = 'save'
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
        if (isNumeric(props.properties[index] )){
            props.properties[index].value = parseFloat(props.properties[index].value);
            if (props.properties[index] .unit == null){
                props.properties[index] .unit = "";
            }
        }
    }
    edited.value.forEach(syncPropertyUpdate);
    deleted.value.forEach(syncPropertyDelete);
    added.value.forEach(syncPropertyCreate);

    state.value = 'view';
}
</script>

<template>
    <b-card>
        <template #header>
            <div class="d-flex">
                <h5 class="flex-grow-1">Properties</h5>
                <b-button size="sm" v-if="state === 'view' && isEditable" @click="enterEditMode"
                    variant="outline-secondary">
                    <i class="fa fa-pen"></i>
                </b-button>
                <b-button-group v-else-if="isEditable" size="sm">
                    <b-button v-if="state === 'edit'" @click="discardChanges" variant="danger">
                        Discard
                    </b-button>
                    <b-button :disabled="!formIsValid" @click="save" variant="success">
                        <b-spinner v-if="state === 'save'" small />
                        SAVE
                    </b-button>
                </b-button-group>
            </div>
        </template>
        <b-card-body>
            edited: {{ edited }} <br>
            deleted: {{ deleted }} <br>
            added: {{ added }}
            <div class="border rounded-3 mb-3 p-3">
                <div class="d-flex">

                    <div class="flex-shrink-1 d-flex">
                        <i class="p-2 align-self-center fa-solid fa-hashtag"></i>
                    </div>
                    <div class="w-25 d-flex ms-1 p-2">
                        <span class="fw-bold">
                            key
                        </span>
                    </div>
                    <div class="w-25 d-flex ms-1 p-2">
                        <span class="fw-bold">
                            value
                        </span>
                    </div>
                    <div class="d-flex ms-1 p-2">
                        <span class="fw-bold">
                            unit
                        </span>
                    </div>
                </div>
                <div v-for="(property, index) in props.properties" :key="property.url">
                    <div v-if="!deleted.includes(index)" class="d-flex">
                        <div class="flex-shrink-1 d-flex">
                            <b-button v-if="state === 'edit'" @click="deleteProperty(index)" class="m-1 align-self-center"
                                size="sm" variant="danger" title="remove property">
                                <i class="fa fa-minus"></i>
                            </b-button>
                            <i v-else class="p-2 align-self-center fa fa-bars"></i>
                        </div>
                        <div class="w-25 d-flex ms-1">
                            <b-form-input v-if="state === 'edit'" @input="editProperty(index)" size="sm"
                                placeholder="Property name" class="align-self-center"
                                v-model="property.name"></b-form-input>
                            <div v-else class="p-2">
                                <span v-if="property.name === ''" class="fw-lighter">
                                    Property name
                                </span>
                                <span v-else>{{ property.name }} </span>
                            </div>
                        </div>
                        <div class="w-25 d-flex ms-1">
                            <b-form-input v-if="state === 'edit'" @input="editProperty(index)" size="sm"
                                placeholder="Property value" class="align-self-center"
                                v-model="property.value"></b-form-input>
                            <div v-else class="p-2">
                                <span v-if="property.value === ''" class="fw-lighter">Property value</span>
                                <span v-else> {{ property.value }} </span>
                            </div>
                        </div>
                        <div v-if="isNumeric(property)" class="d-flex ms-1">
                            <b-form-input v-if="state === 'edit'" @input="editProperty(index)" size="sm"
                                placeholder="dimensionless" class="align-self-center"
                                v-model="property.unit"></b-form-input>
                            <div v-else class="p-2">
                                <span v-if="property.unit === ''" class="fw-lighter"></span>
                                <span v-else> [{{ property.unit }}] </span>
                            </div>
                        </div>
                        <i v-if="edited.includes(index) || added.includes(index)" class="p-2 align-self-center fa fa-upload"></i>
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
            <div v-for="message in messages">
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
}</style>
