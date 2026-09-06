<script setup lang="ts">

import { inject, ref } from "vue";

import { useToast } from "bootstrap-vue-next";

import axios from "axios";
import PublishStage1 from "@/components/publish/PublishStage1.vue";
import PublishStage2 from "@/components/publish/PublishStage2.vue";
import PublishStage3 from "@/components/publish/PublishStage3.vue";
import PublishStage4 from "@/components/publish/PublishStage4.vue";
import PublishProgress from "@/components/publish/PublishProgress.vue";

const props = defineProps({
    user: Object
});

const appProps = inject("appProps") as any;

const toast = useToast();

const stage = ref(0);
const pending_request = ref(false);

let authors: any;
let license: any;

function publish() {
    pending_request.value = true;
    // NOTE: The django view expects the author data in a structure thats not convenient
    // NOTE: for vue. Thats why we transform the structure here.
    const authorsTransformed = authors.map((author: any) => {
        return {
            first_name: author.person.firstName,
            last_name: author.person.lastName,
            orcid_id: author.person.orcidId,
            affiliations: author.affiliations.map((affiliation: any) => {
                return {
                    name: affiliation.name,
                    ror_id: affiliation.rorId
                };
            })
        };
    });
    axios.post("/go/publish/", {
        "surface": appProps.object.id,
        "authors": authorsTransformed,
        "license": license
    }).then((response) => {
        window.location.href = `/ui/dataset-detail/${response.data.dataset_id}/`;
    }).catch((error) => {
        if (error.response?.status == 429) { // Too Many Requests
            toast.create({
                title: "Too many requests",
                body: `Please wait ${error.response.data} seconds before publishing this digital surface twin again.`,
                variant: "danger"
            })?.show();
        } else if (error.response?.status == 403) { // Refused, most likely no ORCID iD
            toast.create({
                title: "Publishing was refused",
                body: error.response.data?.detail
                    ?? "Publishing a dataset requires a connected ORCID iD.",
                variant: "danger"
            })?.show();
        } else {
            toast.create({
                title: "Error",
                body: "An error occurred while publishing the digital surface twin. Please try again later.",
                variant: "danger"
            })?.show();
        }
        pending_request.value = false;
    });
}
</script>

<template>
    <div class="container py-4">
        <div class="card shadow border-0 rounded-4 overflow-hidden">
            <div class="card-header bg-body border-0 pt-4 px-4 pb-0">
                <PublishProgress :stage="stage" />
            </div>
            <div class="card-body p-4 p-md-5">
                <PublishStage1 :stage="stage" :surfaceId="appProps.object.id"
                               @continue="stage = 1"></PublishStage1>
                <PublishStage2 :stage="stage" :user="props.user" @continue="(emitedAuthors) => {
                    authors = emitedAuthors;
                    stage = 2;
                }" @back="stage = 0"></PublishStage2>
                <PublishStage3 :stage="stage" @continue="(emitedLicense) => {
                    license = emitedLicense;
                    stage = 3;
                }" @back="stage = 1"></PublishStage3>
                <PublishStage4 :stage="stage" @back="stage = 2" @publish="publish()"
                               :pending_request="pending_request">
                </PublishStage4>
            </div>
        </div>
    </div>
</template>
