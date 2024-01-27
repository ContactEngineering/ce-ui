<script setup>
import {BCard, BCardBody, BButton, BButtonGroup, BSpinner, BFormInput, BAlert} from 'bootstrap-vue-next';
import {ref, computed} from 'vue';
import axios from "axios";
import cloneDeep from 'lodash/cloneDeep';

const props = defineProps({
    surfaceUrl: String,
    properties: String,
    permission: String
});

// let props.properties = ref(JSON.parse(props.properties));
// this is used as backup of the current props.properties,
let _properties = ref([]);
let editMode = ref(false);
let saving = ref(false);
let warnings = ref([]);
let messages = ref([]);

const showWarning = (msg) => {
    messages.value.push({type: 'warning', visible: true, content: msg});
}

const showError = (msg) => {
    messages.value.push({type: 'danger', visible: true, content: msg});
}

const enterEditMode = () => {
    editMode.value = true;
    // backup props.properties before edit
    _properties = cloneDeep(props.properties);
}

const discardChanges = () => {
    // restore props.properties
    props.properties = []; //cloneDeep(_properties.value);
    editMode.value = false;
}

const saveChanges = () => {
    // Check for empty names and give warning
    if (props.properties.filter((property) => property.name === "").length > 0) {
        showWarning("The property name can not be empty");
    }
    // Check for empty values and give warning
    if (props.properties.filter((property) => property.value === "").length > 0) {
        showWarning("The property value can not be empty");
    }
    // Remove props.properties with empty names of empty values
    props.properties = props.properties.filter((property) => !(property.name === "" || property.value === ""));

    // Patch request to store json String
    // This is just a prove of concept, we should probably save the data in a safer structure...

    saving.value = true;
    axios.patch(props.surfaceUrl, {
       'properties': props.properties
    }).then(response => {
        editMode.value = false;
    }).catch(error => {
        showError("A Error occurred: " + error.message)
    }).finally(() => {
        saving.value = false;
    });
}

const addProperty = () => {
    // Enter editMode
    if (!editMode.value) {
        enterEditMode();
    }
    // Add new empty property if there is no empty last property
    const len = props.properties.length;
    if (len === 0 || (props.properties[len - 1].name != '' && props.properties[len - 1].value != '')) {
        props.properties.push({name: "", value: ""});
    }
}

const removeProperty = (n) => {
    if (n >= 0 && n < props.properties.length) {
        props.properties.splice(n, 1);
    } else {
        console.error('Invalid index');
    }
}

const isEditable = computed(() => {
    return ['edit', 'full'].includes(props.permission);
})

</script>

<template>
    {{ props.properties }} 
    <b-card>
        <template #header>
            <div class="d-flex">
                <h5 class="flex-grow-1">Properties</h5>
                <b-button size="sm" v-if="!editMode && isEditable" @click="enterEditMode" variant="outline-secondary">
                    <i class="fa fa-pen"></i>
                </b-button>
                <b-button-group v-else-if="isEditable" size="sm">
                    <b-button v-if="!saving" @click="discardChanges" variant="danger">
                        Discard
                    </b-button>
                    <b-button @click="saveChanges" variant="success">
                        <b-spinner v-if="saving" small />
                        SAVE
                    </b-button>
                </b-button-group>
            </div>
        </template>
        <b-card-body>
            <div class="border rounded-3 mb-3 p-3">
                <div class="d-flex" v-for="(property, index) in props.properties">
                    <div class="flex-shrink-1 d-flex">
                        <b-button v-if="editMode" @click="removeProperty(index)" class="m-1 align-self-center" size="sm"
                                  variant="danger" title="remove property">
                            <i class="fa fa-minus"></i>
                        </b-button>
                        <i v-else class="p-2 align-self-center fa fa-bars"></i>
                    </div>
                    <div class="w-25 d-flex ms-1">
                        <b-form-input v-if="editMode" size="sm" placeholder="Property name" class="align-self-center"
                                      v-model="property.name"></b-form-input>
                        <div v-else class="p-2">
                            <span v-if="property.name===''" class="fw-lighter">
                                Property name
                            </span>
                            <span v-else>{{ property.name }} </span>
                        </div>
                    </div>
                    <div class="d-flex ms-1">
                        <b-form-input v-if="editMode" size="sm" placeholder="Property value" class="align-self-center"
                                      v-model="property.value"></b-form-input>
                        <div v-else class="p-2">
                            <span v-if="property.value===''" class="fw-lighter">Property value</span>
                            <span v-else> {{ property.value }} </span>
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
    transition: background-color 0.3s; /* Optional: Add a smooth transition effect */
}

.highlight-on-hover:hover {
    border: 1px solid #000000;
    background: var(--bs-secondary-bg-subtle);
    cursor: pointer;
}
</style>
