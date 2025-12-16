<script setup lang="ts">

import {ref} from 'vue';
import { QOptionGroup, QBtn } from 'quasar';

const props = defineProps({
    stage: Number
});
defineEmits(['back', 'continue'])

const ccLicenseOptions = [
    {
        value: "cc0-1.0",
        label: "CC0 1.0",
        description_url: "https://creativecommons.org/publicdomain/zero/1.0/",
        legal_code_url: "https://creativecommons.org/publicdomain/zero/1.0/legalcode",
        title: "CC0 1.0 Universal",
    },
    {
        value: "ccby-4.0",
        label: "CC BY 4.0",
        description_url: "https://creativecommons.org/licenses/by/4.0/",
        legal_code_url: "https://creativecommons.org/licenses/by/4.0/legalcode",
        title: "Creative Commons Attribution 4.0 International Public License",
    },
    {
        value: "ccbysa-4.0",
        label: "CC BY-SA 4.0",
        description_url: "https://creativecommons.org/licenses/by-sa/4.0/",
        legal_code_url: "https://creativecommons.org/licenses/by-sa/4.0/legalcode",
        title: "Creative Commons Attribution-ShareAlike 4.0 International Public License",
    },
];

const selected = ref('cc0-1.0')
</script>
<template>
    <div v-if="props.stage == 2">
        <h2 class="alert-heading">
            Please choose a license
        </h2>
        <div class="flex row justify-center q-my-md">
            <div class="license-options">
                <QOptionGroup
                    v-model="selected"
                    :options="ccLicenseOptions"
                    type="radio"
                >
                    <template v-slot:label="opt">
                        <div class="flex items-center">
                            <span class="license-name q-mr-md" :title="opt.title">
                                {{ opt.label }}
                            </span>
                            <a :href="opt.description_url" class="q-mr-sm">Description</a>
                            <a :href="opt.legal_code_url">Legal code</a>
                        </div>
                    </template>
                </QOptionGroup>
            </div>
        </div>

        <div class="flex row justify-between">
            <QBtn @click="$emit('back')" color="primary" size="lg">
                Back
            </QBtn>
            <QBtn @click="$emit('continue', selected)" color="primary">
                Continue
            </QBtn>
        </div>
    </div>
</template>

<style scoped>
.license-name {
    width: 110px;
    display: inline-block;
}

.license-options {
    max-width: 400px;
}
</style>
