<script setup lang="ts">

import { ref } from 'vue';
import { BFormCheckbox, BButton } from 'bootstrap-vue-next';

const props = defineProps({
    stage: Number,
});

const emit = defineEmits(['back', 'publish']);

const check1 = ref(false);
const valid1 = ref(null);
const check2 = ref(false);
const valid2 = ref(null);

function checkAndPublish() {
    valid1.value = check1.value;
    valid2.value = check2.value;
    if (check1.value && check2.value) {
        emit('publish');
    }
}

</script>
<template>
    <div v-if="stage == 3">
        <h2>Implications of publishing</h2>
        <div class="mt-4">
            <ul>
                <li>The digital twin and all measurements will be <b>visible by
                        everyone</b>,
                    registered or anonymous users, now and in future.
                </li>
                <li>The related data (raw data, descriptions, ..) <b>will be
                        downloadable by everyone</b>.
                </li>
                <li>Every user can perform analyses on your data.</li>
                <li>You choose a license for your data - the choice of the license is
                    irrevocable.
                </li>
                <li>If you have assigned tags to the digital twin or its measurements,
                    these tags are also
                    part of the publication.
                </li>
                <li>Your ORCID iD will saved along with your publication.</li>
                <li>A <a href="https://www.doi.org/">DOI (Digital Object
                        Identifier)</a> will be generated
                    with the given data. Your data will be accessible under the
                    corresponding URL.
                </li>
            </ul>
            <p>
                This is great if you want to <b>make your data public under a permanent
                    URL</b>, e.g. in order
                to reference your data in a citation.
            </p>
            <p>
                Since a copy is made, you can still work on your
                original data as before the publication.
                You may also publish an updated version of this digital surface twin
                later.
            </p>
        </div>
        <div class="d-flex flex-row justify-content-center">
            <div class="d-flex flex-column">
                <BFormCheckbox v-model="check1" :state="valid1">
                    I understand the implications of publishing this digital surface
                    twin and I agree.*<br>
                    <span class="text-muted"> Please read the implications of publishing listed above and check.</span>
                </BFormCheckbox>
                <BFormCheckbox v-model="check2" :state="valid2">
                    I hold copyright of this data or have been authorized by the
                    copyright holders.*<br>
                    <span class="text-muted"> Please make sure you're not publishing data from others without their
                        authorization.
                    </span>
                </BFormCheckbox>
            </div>
        </div>
        <div class="d-flex flex-row justify-content-between">
            <BButton @click="$emit('back')" variant="primary">
                Back
            </BButton>
            <BButton @click="checkAndPublish()" variant="success" size="lg">
                Publish 🚀
            </BButton>
        </div>
    </div>
</template>
