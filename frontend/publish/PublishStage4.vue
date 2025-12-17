<script setup lang="ts">

import { ref } from 'vue';
import { QCheckbox, QBtn, QSpinner } from 'quasar';

const props = defineProps({
    stage: Number,
    pending_request: Boolean
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
        <div class="q-mt-md">
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
        <div class="flex row justify-center">
            <div class="flex column">
                <QCheckbox v-model="check1"
                           :color="valid1 === false ? 'negative' : 'primary'">
                    <span :class="{ 'text-negative': valid1 === false }">
                        I understand the implications of publishing this digital surface
                        twin and I agree.*<br>
                        <span class="text-grey"> Please read the implications of publishing listed above and check.</span>
                    </span>
                </QCheckbox>
                <QCheckbox v-model="check2"
                           :color="valid2 === false ? 'negative' : 'primary'">
                    <span :class="{ 'text-negative': valid2 === false }">
                        I hold copyright of this data or have been authorized by the
                        copyright holders.*<br>
                        <span class="text-grey"> Please make sure you're not publishing data from others without their
                            authorization.
                        </span>
                    </span>
                </QCheckbox>
            </div>
        </div>
        <div class="flex row justify-between q-mt-md">
            <QBtn @click="$emit('back')" color="primary">
                Back
            </QBtn>
            <QBtn v-if="pending_request" disable color="positive" size="lg">
                Publish
                <QSpinner color="white" size="1.2rem" class="q-ml-sm" />
            </QBtn>
            <QBtn v-else @click="checkAndPublish()" color="positive" size="lg">
                Publish
            </QBtn>
        </div>
    </div>
</template>
