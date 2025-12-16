<script setup lang="ts">

import { computed, ref } from 'vue';

import {
    QBtn,
    QBtnGroup,
    QCard,
    QCardSection,
    QInput,
    QSpinner,
    QMarkupTable
} from 'quasar';

import { useNotify } from "@/utils/notify";
import {managerApiSurfacePartialUpdate} from "@/api";
import {getIdFromUrl} from "@/utils/api";

const { show } = useNotify();

const properties = defineModel('properties', {
    default: {}
});

const propertyCount = defineModel("propertyCount", {
    type: Number,
    default: 0
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

const propertiesBeforeEdit = ref<any[]>([]);

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
    if (!_isEditing.value) {
        propertiesBeforeEdit.value = JSON.parse(JSON.stringify(_properties.value));
    }
    _isEditing.value = true;
}

// edit -> view
function discardChanges() {
    // restore properties
    _properties.value = JSON.parse(JSON.stringify(propertiesBeforeEdit.value)); // Deep copy
    _isEditing.value = false;
}

async function save() {
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
    try {
        const surfaceId = getIdFromUrl(props.surfaceUrl);
        const response = await managerApiSurfacePartialUpdate({
            path: {id: surfaceId},
            body: { properties: propertiesArrayToObject(_properties.value) }
        });
        properties.value = response.data["properties"];
        _properties.value = propertiesObjectToArray(response.data["properties"]);
    } catch (error: any) {
        // Restore properties
        _properties.value = propertiesObjectToArray(properties.value);
        const msg = `Upload Failed: ${error.response?.data?.detail}. Please report this bug!`
        show?.({
            props: {
                body: msg,
                variant: "warning"
            }
        });
    } finally {
        _isSaving.value = false;
    }
    propertyCount.value = Object.keys(propertiesArrayToObject(_properties.value)).length; // Update the property count
}

propertyCount.value = Object.keys(properties.value).length // Update the property count

</script>

<template>
    <QCard>
        <QCardSection class="flex items-center">
            <h5 class="col-grow q-ma-none">Properties</h5>
            <QBtn size="sm" v-if="!_isEditing && isEditable" @click="enterEditMode" flat>
                <i class="fa fa-pen"></i>
            </QBtn>
            <QBtnGroup v-else-if="isEditable" flat>
                <QBtn v-if="_isEditing && !_isSaving" @click="discardChanges" color="negative" size="sm">
                    Discard
                </QBtn>
                <QBtn :disable="!formIsValid" @click="save" color="positive" size="sm">
                    <QSpinner v-if="_isSaving" size="1rem" class="q-mr-sm" />
                    SAVE
                </QBtn>
            </QBtnGroup>
        </QCardSection>
        <QCardSection>
            <div v-if="!isEditable && _properties.length === 0">
                This digital surface twin does not have properties.
            </div>
            <QMarkupTable>
                <colgroup>
                    <col />
                    <col />
                    <col />
                    <col />
                </colgroup>
                <thead class="bg-dark text-white">
                    <tr>
                        <th>#</th>
                        <th>Key</th>
                        <th>Value</th>
                        <th>Unit</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(property, index) in _properties" :key="index">
                        <td>
                            <QBtn v-if="_isEditing" @click="deleteProperty(index)" size="sm" color="negative"
                                title="remove property" dense>
                                <i class="fa fa-minus"></i>
                            </QBtn>
                            <i v-else class="fa fa-bars"></i>
                        </td>
                        <td>
                            <QInput v-if="_isEditing" placeholder="Property name" v-model="property.name"
                                    dense outlined />
                            <div v-else>
                                <span v-if="property.name === ''" class="text-grey">
                                    Property name
                                </span>
                                <span v-else>{{ property.name }}</span>
                            </div>
                        </td>
                        <td>
                            <QInput v-if="_isEditing" placeholder="Property value" v-model="property.value"
                                    dense outlined />
                            <div v-else>
                                <span v-if="property.value === ''" class="text-grey">Property value</span>
                                <span v-else>{{ property.value }}</span>
                            </div>
                        </td>
                        <td v-if="isNumeric(property.value)">
                            <QInput v-if="_isEditing" placeholder="dimensionless" v-model="property.unit"
                                    dense outlined />
                            <div v-else>
                                <span v-if="property.unit === '' || property.unit == null"
                                    class="text-grey">(dimensionless)</span>
                                <span v-else>{{ property.unit }}</span>
                            </div>
                        </td>
                        <td v-else>
                            <span class="text-grey">(categorical)</span>
                        </td>
                    </tr>
                </tbody>
            </QMarkupTable>
            <div v-if="isEditable" @click="addProperty" class="flex highlight-on-hover rounded-borders">
                <div class="q-pa-sm">
                    <i class="fa fa-plus"></i>
                </div>
                <div class="q-pa-sm" style="width: 25%;">
                    Add property
                </div>
            </div>
        </QCardSection>
    </QCard>
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
