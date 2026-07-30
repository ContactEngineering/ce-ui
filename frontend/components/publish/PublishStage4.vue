<script setup lang="ts">

import { ref } from 'vue';
import { BFormCheckbox, BButton, BSpinner } from 'bootstrap-vue-next';

const props = defineProps({
    stage: Number,
    pending_request: Boolean
});

const emit = defineEmits(['back', 'publish']);

const check1 = ref(false);
const valid1 = ref<boolean | null>(null);
const check2 = ref(false);
const valid2 = ref<boolean | null>(null);

function checkAndPublish() {
    valid1.value = check1.value;
    valid2.value = check2.value;
    if (check1.value && check2.value) {
        emit('publish');
    }
}

</script>

<template>
    <div v-if="stage == 3" class="stage-container">
        <div class="mb-4">
            <h3 class="fw-bold mb-1">Final Review & Confirmation</h3>
            <p class="text-muted mb-0">Please review the implications of publishing your digital surface twin dataset.</p>
        </div>

        <div class="row g-3 mb-4">
            <div class="col-md-4">
                <div class="card h-100 border-0 bg-light p-3 shadow-sm text-center">
                    <div class="text-primary mb-2">
                        <i class="fa-solid fa-globe fs-2"></i>
                    </div>
                    <h6 class="fw-bold mb-1">Publicly Accessible</h6>
                    <p class="small text-muted mb-0">Visible and downloadable by everyone, including registered and guest users worldwide.</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card h-100 border-0 bg-light p-3 shadow-sm text-center">
                    <div class="text-success mb-2">
                        <i class="fa-solid fa-link fs-2"></i>
                    </div>
                    <h6 class="fw-bold mb-1">Permanent DOI</h6>
                    <p class="small text-muted mb-0">A unique Digital Object Identifier (DOI) will be registered for academic citation.</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card h-100 border-0 bg-light p-3 shadow-sm text-center">
                    <div class="text-warning mb-2">
                        <i class="fa-solid fa-lock-open fs-2"></i>
                    </div>
                    <h6 class="fw-bold mb-1">Irrevocable License</h6>
                    <p class="small text-muted mb-0">Your chosen open license is permanent. An immutable snapshot copy of your data will be created.</p>
                </div>
            </div>
        </div>

        <div class="card border-0 bg-light-subtle p-3 mb-4 rounded-3 shadow-sm">
            <div class="d-flex flex-column gap-3">
                <div class="card p-3 border-2 transition-all cursor-pointer"
                     :class="{ 'border-primary bg-primary-subtle': check1, 'border-danger': valid1 === false, 'border-light-subtle': check1 === false && valid1 !== false }"
                     @click="check1 = !check1">
                    <BFormCheckbox v-model="check1" :state="valid1" class="fw-semibold text-dark" @click.stop>
                        I understand the implications of publishing this digital surface twin dataset and I agree. <span class="text-danger">*</span>
                    </BFormCheckbox>
                    <small class="text-muted ms-4 d-block mt-1">
                        I confirm that I have reviewed the permanent public access and citation implications listed above.
                    </small>
                </div>

                <div class="card p-3 border-2 transition-all cursor-pointer"
                     :class="{ 'border-primary bg-primary-subtle': check2, 'border-danger': valid2 === false, 'border-light-subtle': check2 === false && valid2 !== false }"
                     @click="check2 = !check2">
                    <BFormCheckbox v-model="check2" :state="valid2" class="fw-semibold text-dark" @click.stop>
                        I hold copyright of this data or have been explicitly authorized by the copyright holders. <span class="text-danger">*</span>
                    </BFormCheckbox>
                    <small class="text-muted ms-4 d-block mt-1">
                        Ensure you are not publishing proprietary or restricted third-party data without authorization.
                    </small>
                </div>
            </div>
        </div>

        <div class="d-flex justify-content-between pt-3 border-top">
            <BButton @click="$emit('back')" variant="outline-secondary" size="lg" class="px-4">
                <i class="fa-solid fa-arrow-left me-2"></i> Back
            </BButton>
            
            <BButton v-if="pending_request" disabled variant="success" size="lg" class="px-4">
                <BSpinner small class="me-2" />
                Publishing Snapshot...
            </BButton>
            <BButton v-else @click="checkAndPublish()" variant="success" size="lg" class="px-4 fw-bold shadow-sm">
                Publish Digital Twin 🚀
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
