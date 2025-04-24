<script setup lang="ts">

import { BFormCheckbox, BButton, BSpinner } from 'bootstrap-vue-next';
import { inject, ref } from 'vue';

import { useToastController } from 'bootstrap-vue-next';

import axios from "axios";
import PublishStage1 from '@/publish/PublishStage1.vue';
import PublishStage2 from '@/publish/PublishStage2.vue';
import PublishStage3 from '@/publish/PublishStage3.vue';
import PublishStage4 from '@/publish/PublishStage4.vue';
import ProgessBar from '@/publish/PublishProgess.vue';

const props = defineProps({
    user: Object,
});

const appProps = inject("appProps");

const { show } = useToastController();

const stage = ref(0);
const pending_request = ref(false);

let authors;
let license;

function publish() {
    pending_request.value = true;
    // NOTE: The django view expects the author data in a structure thats not convenient
    // NOTE: for vue. Thats why we transform the structure here.
    const authorsTransformed = authors.map((author) => {
        return {
            first_name: author.person.firstName,
            last_name: author.person.lastName,
            orcid_id: author.person.orcidId,
            affiliations: author.affiliations.map((affiliation) => {
                return {
                    name: affiliation.name,
                    ror_id: affiliation.rorId
                }
            })
        }
    });
    axios.post('/go/publish/', {
        'surface': appProps.object.id,
        'authors': authorsTransformed,
        'license': license
    }).then((response) => {
        window.location.href = `/ui/dataset-detail/${response.data.dataset_id}/`;
    }).catch((error) => {
        if (error.response.status == 429) { // Too Many Requests
            show?.({
                props: {
                    title: "Too many requests",
                    body: `Please wait ${error.response.data} seconds before publishing this digital surface twin again.`,
                    variant: "danger"
                }
            });
        }
        pending_request.value = false;
    });
}
</script>

<template>
    <div class="container">
        <ProgessBar :stage="stage" />
        <div class="p-5">
            <PublishStage1 :stage="stage" :surfaceId="appProps.object.id" @continue="stage = 1"></PublishStage1>
            <PublishStage2 :stage="stage" :user="props.user" @continue="(emitedAuthors) => {
                authors = emitedAuthors;
                stage = 2;
            }" @back="stage = 0"></PublishStage2>
            <PublishStage3 :stage="stage" @continue="(emitedLicense) => {
                license = emitedLicense;
                stage = 3;
            }" @back="stage = 1"></PublishStage3>
            <PublishStage4 :stage="stage" @back="stage = 2" @publish="publish()" :pending_request="pending_request">
            </PublishStage4>
        </div>
    </div>
</template>
