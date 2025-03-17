<script setup lang="ts">

import {ref} from 'vue';
import {BFormRadioGroup, BFormRadio, BButton} from 'bootstrap-vue-next';

const props = defineProps({
    stage: Number
});
defineEmits(['back', 'continue'])

const ccLicenseInfos = [
    {
        key: "cc0-1.0",
        description_url: "https://creativecommons.org/publicdomain/zero/1.0/",
        legal_code_url: "https://creativecommons.org/publicdomain/zero/1.0/legalcode",
        title: "CC0 1.0 Universal",
        option_name: "CC0 1.0",
        spdx_identifier: "CC0-1.0",
    },
    {
        key: "ccby-4.0",
        description_url: "https://creativecommons.org/licenses/by/4.0/",
        legal_code_url: "https://creativecommons.org/licenses/by/4.0/legalcode",
        title: "Creative Commons Attribution 4.0 International Public License",
        option_name: "CC BY 4.0",
        spdx_identifier: "CC-BY-4.0",
    },
    {
        key: "ccbysa-4.0",
        description_url: "https://creativecommons.org/licenses/by-sa/4.0/",
        legal_code_url: "https://creativecommons.org/licenses/by-sa/4.0/legalcode",
        title: "Creative Commons Attribution-ShareAlike 4.0 International Public License",
        option_name: "CC BY-SA 4.0",
        spdx_identifier: "CC-BY-SA-4.0",
    },
];

const selected = ref('cc0-1.0')
</script>
<template>
    <div v-if="props.stage == 2">
        <h2 class="alert-heading">
            Please choose a license
        </h2>
        <div class="d-flex flex-row justify-content-center">
            <BFormRadioGroup v-model="selected" name="radio-stacked" stacked>
                <BFormRadio v-for="license in ccLicenseInfos" :value="license.key">
                    <div class="d-flex">
            <span class=" mr-auto" style="width: 110px;" :title="license.title">
              {{ license.option_name }}
            </span>
                        <span class="me-2">
              <a :href="license.description_url"> Description </a>
            </span>
                        <span>
              <a :href="license.legal_code_url"> Legal code</a>
            </span>
                    </div>
                </BFormRadio>
            </BFormRadioGroup>
        </div>

        <div class="d-flex flex-row justify-content-between">
            <BButton @click="$emit('back')" variant="primary" size="lg">
                Back
            </BButton>
            <BButton @click="$emit('continue', selected)" variant="primary">
                Continue
            </BButton>
        </div>
    </div>
</template>
