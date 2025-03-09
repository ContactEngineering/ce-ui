<script setup>

import axios from "axios";
import { computed, ref } from 'vue';

import {
    BButton,
    BButtonGroup,
    BCard,
    BCardBody,
    BFormInput,
    BSpinner,
    BTableSimple,
    BTbody,
    BTd,
    BTh,
    BThead,
    BTr,
    useToastController
} from 'bootstrap-vue-next';

const { show } = useToastController();

const properties = defineModel('properties', {
    default: {}
});

const props = defineProps({
    surfaceUrl: String,
    permission: String
});

function isNumeric(s) {
    return /^-?\d*\.?\d+$/.test(s);
}

// Convert the properties object (with key-value pairs) to an array (where the key
// is stored as the "name" of the property)
function propertiesObjectToArray(propertiesObject) {
    return Object.entries(propertiesObject).map(([name, property]) => {
        return { name: name, ...property };
    });
}

// Convert the properties array to an object (with key-value pairs)

function propertiesArrayToObject(propertiesArray) {
    let propertiesObject = {};
    for (const property of propertiesArray) {
        const isNumericProperty = isNumeric(property.value);
        let cleanedProperty = {
            value: isNumericProperty ? parseFloat(property.value) : property.value
        };
        if (isNumericProperty) {
            cleanedProperty.unit = property.unit;
        }
        propertiesObject[property.name] = cleanedProperty;
    }
    return propertiesObject;
}

// Is the user currently editing a property?
const _isEditing = ref(false);
// Is a save operation running?
const _isSaving = ref(false);
// This array holds the edited properties
const _properties = ref(propertiesObjectToArray(properties.value));

let formIsValid = computed(() => {
    return true;
});

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

function addProperty() {
    enterEditMode();
    // Add new empty property if there is no empty last property
    const len = _properties.value.length;
    if (len === 0 || (_properties.value[len - 1].name !== "" && _properties.value[len - 1].value !== "")) {
        _properties.value.push({ name: "", value: "", unit: null });
    }
}

function deleteProperty(index) {
    // remove prop
    _properties.value.splice(index, 1);
}

// view -> edit
function enterEditMode() {
    _isEditing.value = true;
}

// edit -> view
function discardChanges() {
    // restore properties
    _properties.value = propertiesObjectToArray(properties.value);
    _isEditing.value = false;
}

function save() {
    // Check for empty names and give warning
    if (_properties.value.filter((property) => property.name === "").length > 0) {
        showWarning("Property names cannot be empty");
        return;
    }
    // Check for empty values and give warning
    if (_properties.value.filter((property) => property.value === "").length > 0) {
        showWarning("Property values can not be empty");
        return;
    }
    // Update properties
    _isEditing.value = false;
    _isSaving.value = true;
    axios.patch(props.surfaceUrl, { properties: propertiesArrayToObject(_properties.value) }).then(response => {
        properties.value = response.data["properties"];
        _properties.value = propertiesObjectToArray(response.data["properties"]);
        _isSaving.value = false;
    });
}

</script>

<template>
    <BCard>
        <template #header>
            <div class="d-flex">
                <h5 class="flex-grow-1">Properties</h5>
                <BButton size="sm" v-if="!_isEditing && isEditable" @click="enterEditMode" variant="outline-secondary">
                    <i class="fa fa-pen"></i>
                </BButton>
                <BButtonGroup v-else-if="isEditable" size="sm">
                    <BButton v-if="_isEditing && !_isSaving" @click="discardChanges" variant="danger">
                        Discard
                    </BButton>
                    <BButton :disabled="!formIsValid" @click="save" variant="success">
                        <BSpinner v-if="_isSaving" small />
                        SAVE
                    </BButton>
                </BButtonGroup>
            </div>
        </template>
        <BCardBody>
            <div v-if="!isEditable && _properties.length === 0">
                This digital surface twin does not have properties.
            </div>
            <BTableSimple>
                <colgroup>
                    <col />
                    <col />
                    <col />
                    <col />
                </colgroup>
                <BThead head-variant="dark">
                    <BTr>
                        <BTh>#</BTh>
                        <BTh>Key</BTh>
                        <BTh>Value</BTh>
                        <BTh>Unit</BTh>
                    </BTr>
                </BThead>
                <BTbody>
                    <BTr v-for="(property, index) in _properties">
                        <BTd>
                            <BButton v-if="_isEditing" @click="deleteProperty(index)" size="sm" variant="danger"
                                title="remove property">
                                <i class="fa fa-minus"></i>
                            </BButton>
                            <i v-else class="fa fa-bars"></i>
                        </BTd>
                        <BTd>
                            <BFormInput v-if="_isEditing" placeholder="Property name" v-model="property.name">
                            </BFormInput>
                            <div v-else>
                                <span v-if="property.name === ''" class="fw-lighter">
                                    Property name
                                </span>
                                <span v-else>{{ property.name }}</span>
                            </div>
                        </BTd>
                        <BTd>
                            <BFormInput v-if="_isEditing" placeholder="Property value" v-model="property.value">
                            </BFormInput>
                            <div v-else>
                                <span v-if="property.value === ''" class="fw-lighter">Property value</span>
                                <span v-else>{{ property.value }}</span>
                            </div>
                        </BTd>
                        <BTd v-if="isNumeric(property.value)">
                            <BFormInput v-if="_isEditing" placeholder="dimensionless" v-model="property.unit">
                            </BFormInput>
                            <div v-else>
                                <span v-if="property.unit === '' || property.unit == null"
                                    class="text-muted">(dimensionless)</span>
                                <span v-else>{{ property.unit }}</span>
                            </div>
                        </BTd>
                        <BTd v-else>
                            <span class="text-muted">(categorical)</span>
                        </BTd>
                    </BTr>
                </BTBody>
            </BTableSimple>
            <div v-if="isEditable" @click="addProperty" class="d-flex highlight-on-hover rounded-3">
                <div class="p-2 flex-shrink-1">
                    <i class="fa fa-plus"></i>
                </div>
                <div class="w-25 p-2">
                    Add property
                </div>
            </div>
        </BCardBody>
    </BCard>
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
