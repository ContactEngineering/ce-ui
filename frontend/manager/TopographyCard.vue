<script setup lang="ts">

import {computed, onMounted, onBeforeUnmount} from "vue";

import {managerApiTopographyRetrieve} from "@/api";
import {getIdFromUrl} from "@/utils/api";

import TopographyErrorCard from "./TopographyErrorCard.vue";
import TopographyPendingCard from "./TopographyPendingCard.vue";
import TopographyUpdateCard from "./TopographyUpdateCard.vue";
import TopographyUploadCard from "./TopographyUploadCard.vue";

const props = defineProps({
    disabled: {
        type: Boolean,
        default: false
    },
    enlarged: {
        type: Boolean,
        default: false
    },
    pollingInterval: {
        type: Number,
        default: 1000  // milliseconds
    },
    selectable: {
        type: Boolean,
        default: false
    },
    selected: {
        type: Boolean,
        default: false
    },
    topography: {
        type: Object,
        default: null
    },
    topographyUrl: {
        type: String,
        default: null
    },
    syncTab: {
    type: Boolean,
    default: false
    }
});

const emit = defineEmits([
    'delete:topography',
    'update:topography',
    'update:selected'
]);

let _currentTimeout = null;

onMounted(() => {
    scheduleStateCheck(props.topography);
});

onBeforeUnmount(() => {
    if (_currentTimeout != null) {
        clearTimeout(_currentTimeout);
        _currentTimeout = null;
    }
});

const isUploading = computed(() => {
    return props.topography !== null && props.topography.datafile.upload_instructions != null;
});

function scheduleStateCheck(topography) {
    if (topography === null) {
        checkState();
    } else if (topography.datafile.upload_instructions == null && ['no', 'pe', 'st'].includes(topography.task_state)) {
        if (_currentTimeout != null) {
            clearTimeout(_currentTimeout);
        }
        _currentTimeout = setTimeout(checkState, props.pollingInterval);
    }
}

async function checkState() {
    const topographyId = getIdFromUrl(props.topographyUrl);
    const response = await managerApiTopographyRetrieve({path: {id: topographyId}});
    emit('update:topography', response.data);
    scheduleStateCheck(response.data);
}

function topographyDeleted(url) {
    emit('delete:topography', url);
}

const topographyModel = computed({
    get() {
        scheduleStateCheck(props.topography);
        return props.topography;
    },
    set(value) {
        emit('update:topography', value);
        scheduleStateCheck(value);
    }
});

const selectedModel = computed({
    get() {
        return props.selected;
    },
    set(value) {
        emit('update:selected', value);
    }
});

const activeTab = defineModel('activeTab', {
    type: String,
    default: 'home'
});


</script>

<template>
    <TopographyUploadCard
        v-if="topography !== null && isUploading"
        @delete:topography="topographyDeleted"
        v-model:topography="topographyModel">
    </TopographyUploadCard>
    <TopographyPendingCard
        v-if="topography !== null && !isUploading && topography.task_state !== 'su' && topography.task_state !== 'fa'"
        :url="topographyUrl"
        :name="topography.name"
        :task-state="topography.task_state"
        @delete:topography="topographyDeleted"
        v-model:topography="topographyModel">
    </TopographyPendingCard>
    <TopographyErrorCard
        v-if="topography !== null && !isUploading && topography.task_state === 'fa'"
        :topography-url="topographyUrl"
        :topography="topography"
        @delete:topography="topographyDeleted"
        v-model:topography="topographyModel">
    </TopographyErrorCard>
    <TopographyUpdateCard
        v-if="topography !== null && !isUploading && topography.task_state === 'su'"
        :topography-url="topographyUrl"
        :topography="topography"
        :disabled="disabled"
        :enlarged="enlarged"
        :selectable="selectable"
        :syncTab="syncTab"
        @delete:topography="topographyDeleted"
        v-model:active-tab="activeTab"
        v-model:topography="topographyModel"
        v-model:selected="selectedModel">
    </TopographyUpdateCard>
</template>
