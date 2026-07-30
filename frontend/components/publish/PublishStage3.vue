<script setup lang="ts">

import { ref } from 'vue';
import { BFormRadio, BButton } from 'bootstrap-vue-next';

const props = defineProps({
    stage: Number
});
defineEmits(['back', 'continue']);

const ccLicenseInfos = [
    {
        key: "cc0-1.0",
        description_url: "https://creativecommons.org/publicdomain/zero/1.0/",
        legal_code_url: "https://creativecommons.org/publicdomain/zero/1.0/legalcode",
        title: "CC0 1.0 Universal",
        option_name: "CC0 1.0",
        summary: "Public domain: anyone may use the data for any purpose, no attribution required.",
        spdx_identifier: "CC0-1.0",
        recommended: true
    },
    {
        key: "ccby-4.0",
        description_url: "https://creativecommons.org/licenses/by/4.0/",
        legal_code_url: "https://creativecommons.org/licenses/by/4.0/legalcode",
        title: "Creative Commons Attribution 4.0 International Public License",
        option_name: "CC BY 4.0",
        summary: "Free to reuse and adapt, as long as credit is given (attribution).",
        spdx_identifier: "CC-BY-4.0",
        recommended: false
    },
    {
        key: "ccbysa-4.0",
        description_url: "https://creativecommons.org/licenses/by-sa/4.0/",
        legal_code_url: "https://creativecommons.org/licenses/by-sa/4.0/legalcode",
        title: "Creative Commons Attribution-ShareAlike 4.0 International Public License",
        option_name: "CC BY-SA 4.0",
        summary: "Reuse and adapt with attribution, but derivatives must keep the same license (share-alike).",
        spdx_identifier: "CC-BY-SA-4.0",
        recommended: false
    },
];

const selected = ref('cc0-1.0');
</script>

<template>
    <div v-if="props.stage == 2" class="stage-container">
        <div class="mb-4">
            <h3 class="fw-bold mb-1">Select a Dataset License</h3>
            <p class="text-muted mb-0">Choose an open license governing how researchers and the public can reuse this digital twin data.</p>
        </div>

        <div class="row g-3 mb-4">
            <div v-for="license in ccLicenseInfos" :key="license.key" class="col-12">
                <div class="card h-100 cursor-pointer border-2 transition-all shadow-sm"
                     :class="{ 'border-primary bg-primary-subtle': selected === license.key, 'border-light-subtle': selected !== license.key }"
                     @click="selected = license.key">
                    <div class="card-body d-flex align-items-start p-3">
                        <BFormRadio v-model="selected" :value="license.key" name="license-selection" class="me-3 mt-1" />
                        <div class="flex-grow-1">
                            <div class="d-flex align-items-center justify-content-between mb-1">
                                <h5 class="card-title mb-0 fw-bold text-dark">
                                    {{ license.option_name }} <span class="text-muted fs-6 fw-normal">— {{ license.title }}</span>
                                </h5>
                                <span v-if="license.recommended" class="badge bg-success-subtle text-success border border-success-subtle ms-2">
                                    <i class="fa-solid fa-star me-1"></i> Recommended
                                </span>
                            </div>
                            <p class="card-text text-body-secondary mb-2">{{ license.summary }}</p>
                            <div class="d-flex gap-2">
                                <a :href="license.description_url" target="_blank" rel="noopener" class="btn btn-sm btn-outline-secondary py-0 px-2" @click.stop>
                                    Description <i class="fa-solid fa-arrow-up-right-from-square ms-1"></i>
                                </a>
                                <a :href="license.legal_code_url" target="_blank" rel="noopener" class="btn btn-sm btn-outline-secondary py-0 px-2" @click.stop>
                                    Legal Code <i class="fa-solid fa-scale-balanced ms-1"></i>
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="d-flex justify-content-between pt-3 border-top">
            <BButton @click="$emit('back')" variant="outline-secondary" size="lg" class="px-4">
                <i class="fa-solid fa-arrow-left me-2"></i> Back
            </BButton>
            <BButton @click="$emit('continue', selected)" variant="primary" size="lg" class="px-4">
                Continue to Submit <i class="fa-solid fa-arrow-right ms-2"></i>
            </BButton>
        </div>
    </div>
</template>

<style scoped>
.cursor-pointer {
    cursor: pointer;
}
.transition-all {
    transition: all 0.2s ease-in-out;
}
</style>
