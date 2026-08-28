<script setup lang="ts">

import axios from "axios";
import {computed, onBeforeUnmount, watch} from "vue";

import TopographyErrorCard from "@/components/manager/TopographyErrorCard.vue";
import TopographyPendingCard from "@/components/manager/TopographyPendingCard.vue";
import TopographyUpdateCard from "@/components/manager/TopographyUpdateCard.vue";
import TopographyUploadCard from "@/components/manager/TopographyUploadCard.vue";

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
        // Every pending measurement on the dataset page polls its own state;
        // one request per second per measurement adds up quickly during bulk
        // uploads
        default: 3000  // milliseconds
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

onBeforeUnmount(() => {
    if (_currentTimeout != null) {
        clearTimeout(_currentTimeout);
        _currentTimeout = null;
    }
});

const isUploading = computed(() => {
    return props.topography !== null && props.topography.datafile?.upload_instructions != null;
});

function scheduleStateCheck(topography) {
    if (_currentTimeout != null) {
        clearTimeout(_currentTimeout);
        _currentTimeout = null;
    }
    if (topography != null && topography.datafile?.upload_instructions == null && ['no', 'pe', 'st'].includes(topography.task_state)) {
        _currentTimeout = setTimeout(checkState, props.pollingInterval);
    }
}

function checkState() {
    if (!props.topographyUrl) {
        return;
    }
    axios.get(props.topographyUrl).then(response => {
        emit('update:topography', response.data);
    }).catch(() => {
        if (_currentTimeout != null) {
            clearTimeout(_currentTimeout);
            _currentTimeout = null;
        }
    });
}

watch(() => props.topography, (newTopography) => {
    scheduleStateCheck(newTopography);
}, { immediate: true });

function topographyDeleted(url) {
    emit('delete:topography', url);
}

const topographyModel = computed({
    get() {
        return props.topography;
    },
    set(value) {
        emit('update:topography', value);
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
