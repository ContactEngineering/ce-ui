<script setup>
import axios from "axios";
import { ref, computed } from 'vue';
import { BCard, BCardBody, BButton, BButtonGroup, BSpinner, BFormInput, BAlert } from 'bootstrap-vue-next';
const props = defineProps({
    surfaceUrl: String,
    permission: String
});

let properties = ref({});
let propertiesTable = ref([]);

function pullProperties() {
    return axios.get(props.surfaceUrl).then((res) => {
        properties.value = res.data.properties;
    });
}

function syncPropertiesTable() {
    propertiesTable.value = Object.entries(properties.value).map(([key, value]) => {
        return {
            name: key,
            value: value.value,
            unit: value.unit
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

function isNumeric(property) {
    return /^-?\d*\.?\d+$/.test(property.value);
}

function enterEditMode() {
    if (!_isEditing.value) {
        _isEditing.value = true;
        syncPropertiesTable();
    }
}

function discardChanges() {
    syncPropertiesTable();
    _isEditing.value = false;
}

function addProperty() {
    enterEditMode();
    propertiesTable.value.push({ name: "", value: "", unit: "" });
}

function deleteProperty(index) {
    propertiesTable.value.splice(index, 1);
}

const formIsValid = computed(() => {
    // Property names and values cant be empty
    const emptyFields = propertiesTable.value.some((property) => {
        return property.name === "" || property.value === "";
    })

    //Property names should be uniqe for a digital surface twin
    const hashMap = {}
    const nameDuplicates = propertiesTable.value.some(property => {
        if (hashMap[property.name]) {
            return true
        }
        hashMap[property.name] = true;

    });

    return !(emptyFields || nameDuplicates);

});

const isEditable = computed(() => {
    return ['edit', 'full'].includes(props.permission);
});

function save() {
    const propertiesDict = {};
    propertiesTable.value.forEach((property) => {
        if (isNumeric(property)) {
            propertiesDict[property.name] = {
                value: parseFloat(property.value),
                unit: property.unit
            };
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
                <b-button size="sm" v-if="!_isEditing && isEditable" @click="enterEditMode" variant="outline-secondary">
                    <i class="fa fa-pen"></i>
                </b-button>
                <b-button-group v-else size="sm">
                    <b-button v-if="_isEditing" @click="discardChanges" variant="danger">
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
            <div v-if="!isEditable && !properties">
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

                <div v-for="(property, index) in propertiesTable" class="d-flex">
                    <div class="flex-shrink-1 d-flex">
                        <b-button v-if="_isEditing" @click="deleteProperty(index)" class="m-1 align-self-center"
                            size="sm" variant="danger" title="remove property">
                            <i class="fa fa-minus"></i>
                        </b-button>
                        <i v-else class="p-2 align-self-center fa fa-bars"></i>
                    </div>
                    <div class="w-25 d-flex ms-1">
                        <b-form-input v-if="_isEditing" v-model="property.name" size="sm" placeholder="Property name"
                            class="align-self-center">
                        </b-form-input>
                        <div v-else class="p-2">
                            <span v-if="property.name === ''" class="fw-lighter">
                                Property name
                            </span>
                            <span v-else>{{ property.name }}</span>
                        </div>
                    </div>
                    <div class="w-25 d-flex ms-1">
                        <b-form-input v-if="_isEditing" size="sm" placeholder="Property value" class="align-self-center"
                            v-model="property.value"></b-form-input>
                        <div v-else class="p-2">
                            <span v-if="property.value === ''" class="fw-lighter">Property value</span>
                            <span v-else>{{ property.value }}</span>
                        </div>
                    </div>
                    <div v-if="isNumeric(property)" class="d-flex ms-1">
                        <b-form-input v-if="_isEditing" size="sm" placeholder="dimensionless" class="align-self-center"
                            v-model="property.unit"></b-form-input>
                        <div v-else class="p-2">
                            <span v-if="property.unit === ''" class="fw-lighter"></span>
                            <span v-else>{{ property.unit }}</span>
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
