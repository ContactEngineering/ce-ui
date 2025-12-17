<script setup lang="ts">

import { computed, inject, onMounted, ref } from "vue";

import { QCheckbox } from "quasar";

import { analysisApiWorkflowList } from "@/api";

import { subjectsFromBase64 } from "../utils/api";
import { useAnalysisStore } from "topobank/stores/analysis";

const analysis = useAnalysisStore();

const props = defineProps({
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

onMounted(async () => {
    const response = await analysisApiWorkflowList();
    _cards.value = response.data;
});

function toggleWorkflow(cardName: string, checked: boolean) {
    if (checked && !analysis.workflows.includes(cardName)) {
        analysis.workflows.push(cardName);
    } else if (!checked) {
        const index = analysis.workflows.indexOf(cardName);
        if (index > -1) {
            analysis.workflows.splice(index, 1);
        }
    }
}

</script>

<template>
    <div class="row q-mb-md">
        <div class="col-12 flex flex-wrap q-gutter-md">
            <QCheckbox v-for="card in _cards"
                       :key="card.name"
                       :model-value="analysis.isSelected(card.name)"
                       :label="card.display_name"
                       @update:model-value="(val) => toggleWorkflow(card.name, val)" />
        </div>
    </div>
    <div class="row">
        <div v-for="card in _cards"
             :key="card.name"
             :class="{ 'col-lg-6': true, 'q-mb-lg': true }"
             :style="{ display: analysis.isSelected(card.name) ? 'block' : 'none' }">
            <component :is="`${card.visualization_type}-card`"
                       v-if="analysis.isSelected(card.name)"
                       :enlarged="false"
                       :function-name="card.name"
                       :subjects="subjectsDict">
            </component>
        </div>
    </div>
</template>
