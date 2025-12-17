<script lang="ts">

import {
    QBanner,
    QBtn,
    QBtnGroup,
    QCard,
    QCardSection,
    QInput,
    QSelect,
    QSpinner
} from "quasar";

import {managerApiSurfacePartialUpdate} from "@/api";
import {getIdFromUrl} from "@/utils/api";

import TipTapEditor from "./TipTapEditor.vue";

export default {
    name: "surface-description",
    components: {
        QBanner,
        QBtn,
        QBtnGroup,
        QCard,
        QCardSection,
        QInput,
        QSelect,
        QSpinner,
        TipTapEditor
    },
    props: {
        category: String,
        description: String,
        name: String,
        permission: String,
        surfaceUrl: String,
        tags: Object
    },
    data() {
        return {
            _category: this.category,
            _description: this.description,
            _editing: false,
            _error: null,
            _name: this.name,
            _options: [
                { value: "exp", label: "Experimental data" },
                { value: "sim", label: "Simulated data" },
                { value: "dum", label: "Dummy data" }
            ],
            _savedDescription: this.description,
            _savedName: this.name,
            _saving: false,
            _tags: this.tags,
            _tagsInput: Array.isArray(this.tags) ? this.tags.join(', ') : ''
        };
    },
    methods: {
        async saveCard() {
            this._editing = false;
            this._saving = true;
            // Parse tags from comma-separated input
            this._tags = this._tagsInput.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0);
            try {
                const surfaceId = getIdFromUrl(this.surfaceUrl);
                const response = await managerApiSurfacePartialUpdate({
                    path: {id: surfaceId},
                    body: {
                        name: this._name,
                        description: this._description,
                        category: this._category,
                        tags: this._tags
                    }
                });
                this._error = null;
                this.$emit("surface-updated", response.data);
            } catch (error) {
                this._error = error;
                this._name = this._savedName;
                this._description = this._saveDescription;
            } finally {
                this._saving = false;
            }
        }
    },
    computed: {
        isEditable() {
            return this.permission !== "view";
        }
    }
};
</script>

<template>
    <QCard>
        <QCardSection class="flex items-center">
            <h5 class="col-grow q-ma-none">Description</h5>
            <QBtnGroup v-if="!_editing && !_saving && isEditable" flat>
                <QBtn flat size="sm" icon="edit"
                      @click="_savedName = `${_name}`; _savedDescription = `${_description}`; _editing = true" />
            </QBtnGroup>
            <QBtnGroup v-if="_editing || _saving" flat>
                <QBtn v-if="_editing"
                      color="negative" size="sm"
                      @click="_editing = false; _name = _savedName; _description = _savedDescription">
                    Discard
                </QBtn>
                <QBtn color="positive" size="sm"
                      @click="saveCard">
                    <QSpinner v-if="_saving" size="1rem" class="q-mr-sm" />
                    SAVE
                </QBtn>
            </QBtnGroup>
        </QCardSection>
        <QCardSection>
            <QBanner v-if="_error !== null" class="bg-negative text-white q-mb-md">
                {{ _error?.message }}
            </QBanner>
            <div class="q-mb-md">
                <label class="text-weight-medium">Name</label>
                <QInput v-model="_name"
                        placeholder="Please enter a name here"
                        :disable="!_editing"
                        dense outlined />
                <div class="text-caption text-grey">A short, descriptive name for this digital surface twin</div>
            </div>
            <div class="q-mb-md">
                <label class="text-weight-medium">Description</label>
                <TipTapEditor v-model="_description"
                              :disabled="!_editing" />
                <div class="text-caption text-grey">Arbitrary descriptive text, ideally including information on specimen preparation, measurement conditions, etc.</div>
            </div>
            <div class="q-mb-md">
                <label class="text-weight-medium">Category</label>
                <QSelect v-model="_category"
                         :options="_options"
                         :disable="!_editing"
                         emit-value
                         map-options
                         dense outlined />
                <div class="text-caption text-grey">Please indicate the category of the data contained in this digital surface twin.</div>
            </div>
            <div class="q-mb-md">
                <label class="text-weight-medium">Tags</label>
                <QInput v-model="_tagsInput"
                        :disable="!_editing"
                        placeholder="Enter tags separated by commas"
                        dense outlined />
                <div class="text-caption text-grey">Attach arbitrary tags (labels) to this digital surface twin. Tags can be hierachical (like a directory structure); separate hierarchies with a /, e.g. 'bear/foot/nail' may indicate a set of topography scans on the nail of a bear foot.</div>
            </div>
        </QCardSection>
    </QCard>
</template>
