<script setup lang="ts">

import axios from "axios";
import {computed, inject, onMounted, ref} from "vue";

import {
    BForm,
    BFormCheckbox,
    BFormCheckboxGroup,
    BFormGroup,
} from "bootstrap-vue-next";

import {subjectsFromBase64} from "@/utils/api";
import {useAnalysisStore} from "@/stores/analysis";

const analysis = useAnalysisStore();

const props = defineProps({
    apiRegistryUrl: {
        type: String,
        default: '/analysis/api/workflow/'
    },
    subjects: String
});

const appProps = inject("appProps");

const _cards = ref([]);

function getSubjectsDict() {
    let subjects = appProps.searchParams.get("subjects");
    if (props.subjects != null) {
        subjects = props.subjects;
    }
    if (subjects != null) {
        return subjectsFromBase64(subjects);
    }
    return null;
}

const subjectsDict = computed(() => {
    return getSubjectsDict();
});

// Number of workflows that are currently shown, out of those on offer
const nbSelected = computed(() => {
    return _cards.value.filter(card => analysis.isSelected(card.name)).length;
});

/* Select or deselect every workflow at once. Picking twenty workflows one by
   one is the tedious part of this page, and the state in between is what the
   checkbox shows as indeterminate. */
const allSelected = computed({
    get() {
        return _cards.value.length > 0 && nbSelected.value === _cards.value.length;
    },
    set(value: boolean) {
        if (value) {
            analysis.selectAll(_cards.value.map(card => card.name));
        } else {
            analysis.clear();
        }
    }
});

const someSelected = computed(() => {
    return nbSelected.value > 0 && nbSelected.value < _cards.value.length;
});

// Position of each card among the *visible* (selected) cards, so the
// alternating background stripes the shown cards correctly even when some
// workflows are hidden.
const visibleIndex = computed(() => {
    const index = {};
    let i = 0;
    for (const card of _cards.value) {
        if (analysis.isSelected(card.name)) {
            index[card.name] = i++;
        }
    }
    return index;
});

onMounted(() => {
    let queryParams = '';
    axios.get(`${props.apiRegistryUrl}${queryParams}`).then(response => {
        _cards.value = response.data;
    });
});

</script>

<template>
    <div class="row mb-2">
        <BForm class="col-12">
            <BFormGroup>
                <BFormCheckbox v-model="allSelected"
                               :disabled="_cards.length === 0"
                               :indeterminate="someSelected">
                    Select all
                    <span v-if="nbSelected > 0" class="text-secondary">
                        ({{ nbSelected }} of {{ _cards.length }} selected)
                    </span>
                </BFormCheckbox>
                <hr class="my-2">
                <BFormCheckboxGroup v-model="analysis.workflows">
                    <BFormCheckbox v-for="card in _cards"
                                   :key="card.name"
                                   :value="card.name">
                        {{ card.display_name }}
                    </BFormCheckbox>
                </BFormCheckboxGroup>
            </BFormGroup>
        </BForm>
    </div>
    <div class="row">
        <div v-for="card in _cards"
             :key="card.name"
             :class="{ 'col-lg-6': true, 'mb-4': true, 'd-none': !analysis.isSelected(card.name) }">
            <!-- Left accent bar (primary) plus alternating background visually
                 separate each analysis card, matching the measurement list. -->
            <div class="border-start border-primary border-4 ps-3 h-100"
                 :class="visibleIndex[card.name] % 2 === 0 ? 'bg-body' : 'bg-body-tertiary'">
                <component :is="`${card.visualization_type}-card`"
                           v-if="analysis.isSelected(card.name)"
                           :enlarged="false"
                           :function-name="card.name"
                           :description="card.description"
                           :reference-url="card.reference_url"
                           :subjects="subjectsDict">
                </component>
            </div>
        </div>
    </div>
</template>
