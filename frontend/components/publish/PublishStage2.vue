<script setup lang="ts">

import { computed, inject, ref } from "vue";
import { BCard, BButton, BButtonGroup, BFormInput, BFormInvalidFeedback, BAlert } from "bootstrap-vue-next";

import HelpTooltip from "@/components/ui/HelpTooltip.vue";

import {
    type Author,
    emptyAffiliation,
    emptyAuthor,
    formatAuthorList,
    validateAuthors
} from "@/utils/authors";

const props = defineProps({
    stage: Number
});

const appProps = inject("appProps") as any;

const emit = defineEmits(["back", "continue"]);

const authors = ref<Author[]>([emptyAuthor()]);

function fillAuthor(index: number) {
    authors.value[index].person = {
        firstName: appProps?.userFirstName || "",
        firstNameValid: null,
        lastName: appProps?.userLastName || "",
        lastNameValid: null,
        orcidId: appProps?.userOrcid || "",
        orcidIdValid: null
    };
}

function addAuthor() {
    authors.value.push(emptyAuthor());
}

function addAffiliation(index: number) {
    authors.value[index].affiliations.push(emptyAffiliation());
}

function removeAuthor(index: number) {
    authors.value.splice(index, 1);
}

function removeAffiliation(authorIndex: number, affiliationIndex: number) {
    if (authorIndex >= 0 && authorIndex < authors.value.length) {
        authors.value[authorIndex].affiliations.splice(affiliationIndex, 1);
    }
}

function moveAuthorUp(index: number) {
    if (index > 0 && index < authors.value.length) {
        [authors.value[index], authors.value[index - 1]] =
            [authors.value[index - 1], authors.value[index]];
    }
}

function moveAffiliationUp(authorIndex: number, affiliationIndex: number) {
    if (authorIndex >= 0 && authorIndex < authors.value.length) {
        const affiliations = authors.value[authorIndex].affiliations;
        if (affiliationIndex > 0 && affiliationIndex < affiliations.length) {
            [affiliations[affiliationIndex], affiliations[affiliationIndex - 1]] =
                [affiliations[affiliationIndex - 1], affiliations[affiliationIndex]];
        }
    }
}

function moveAuthorDown(index: number) {
    if (index >= 0 && index < authors.value.length - 1) {
        [authors.value[index], authors.value[index + 1]] =
            [authors.value[index + 1], authors.value[index]];
    }
}

function moveAffiliationDown(authorIndex: number, affiliationIndex: number) {
    if (authorIndex >= 0 && authorIndex < authors.value.length) {
        const affiliations = authors.value[authorIndex].affiliations;
        if (affiliationIndex >= 0 && affiliationIndex < affiliations.length - 1) {
            [affiliations[affiliationIndex], affiliations[affiliationIndex + 1]] =
                [affiliations[affiliationIndex + 1], affiliations[affiliationIndex]];
        }
    }
}

function nextStage() {
    if (!validateAuthors(authors.value)) {
        return;
    }
    emit("continue", authors.value);
}

const authorsString = computed(() => formatAuthorList(authors.value));

</script>

<template>
    <div v-if="props.stage == 1" class="stage-container">
        <div class="d-flex align-items-center justify-content-between mb-3">
            <div>
                <h3 class="fw-bold mb-1">Author Details</h3>
                <p class="text-muted mb-0">Specify the primary authors and institutional affiliations for this dataset citation.</p>
            </div>
        </div>

        <BAlert :model-value="true" variant="primary" class="border-primary-subtle bg-primary-subtle text-primary-emphasis mb-4 shadow-sm">
            <div class="d-flex align-items-center">
                <i class="fa-solid fa-quote-left fs-4 me-3 text-primary"></i>
                <div>
                    <strong class="d-block small text-uppercase tracking-wide text-primary">Citation Preview</strong>
                    <span class="fs-6 fw-semibold">{{ authorsString || "No authors entered yet" }}</span>
                </div>
            </div>
        </BAlert>

        <div class="authors-list mb-4">
            <BCard v-for="(author, index) in authors" :key="index" class="mb-3 shadow-sm border">
                <template #header>
                    <div class="d-flex align-items-center justify-content-between">
                        <div class="d-flex align-items-center">
                            <span class="badge bg-primary me-2 fs-6">{{ index + 1 }}</span>
                            <h6 class="mb-0 fw-bold">Author #{{ index + 1 }}</h6>
                        </div>
                        <div class="d-flex align-items-center gap-2">
                            <BButton @click="fillAuthor(index)" variant="outline-primary" size="sm"
                                     title="Autofill with your logged-in profile name & ORCID">
                                <i class="fa-solid fa-user-check me-1"></i>
                                Autofill My Profile
                            </BButton>
                            <BButtonGroup size="sm">
                                <BButton :disabled="index == 0" @click="moveAuthorUp(index)" variant="outline-secondary" title="Move author up">
                                    <i class="fa-solid fa-arrow-up"></i>
                                </BButton>
                                <BButton :disabled="index == authors.length - 1" @click="moveAuthorDown(index)" variant="outline-secondary" title="Move author down">
                                    <i class="fa-solid fa-arrow-down"></i>
                                </BButton>
                            </BButtonGroup>
                            <BButton :disabled="authors.length == 1" @click="removeAuthor(index)" variant="outline-danger" size="sm" title="Remove author">
                                <i class="fa-solid fa-trash-can"></i>
                            </BButton>
                        </div>
                    </div>
                </template>

                <div class="row g-3">
                    <div class="col-md-4">
                        <label class="form-label fw-semibold small">First Name <span class="text-danger">*</span></label>
                        <BFormInput v-model="author.person.firstName"
                                    :state="author.person.firstNameValid"
                                    placeholder="e.g. Jane">
                        </BFormInput>
                        <BFormInvalidFeedback>First name is required.</BFormInvalidFeedback>
                    </div>
                    <div class="col-md-4">
                        <label class="form-label fw-semibold small">Last Name <span class="text-danger">*</span></label>
                        <BFormInput v-model="author.person.lastName"
                                    :state="author.person.lastNameValid"
                                    placeholder="e.g. Doe">
                        </BFormInput>
                        <BFormInvalidFeedback>Last name is required.</BFormInvalidFeedback>
                    </div>
                    <div class="col-md-4">
                        <label class="form-label fw-semibold small d-flex align-items-center">
                            ORCID iD
                            <HelpTooltip label="What is an ORCID iD?"
                                text="An ORCID iD is a free, unique identifier for researchers that permanently links you to your work — regardless of name changes or spellings."
                                link-url="https://orcid.org/"
                                link-text="orcid.org"/>
                        </label>
                        <BFormInput v-model="author.person.orcidId"
                                    :state="author.person.orcidIdValid"
                                    placeholder="0000-0000-0000-0000">
                        </BFormInput>
                        <BFormInvalidFeedback>Must be a valid 16-digit ORCID iD (e.g. 0000-0002-1825-0097).</BFormInvalidFeedback>
                    </div>
                </div>

                <div class="affiliations-section mt-4 pt-3 border-top">
                    <div class="d-flex align-items-center justify-content-between mb-2">
                        <h6 class="mb-0 fw-semibold text-secondary">
                            <i class="fa-solid fa-building-columns me-1"></i>
                            Affiliations ({{ author.affiliations.length }})
                        </h6>
                        <BButton @click="addAffiliation(index)" variant="outline-success" size="sm">
                            <i class="fa-solid fa-plus me-1"></i> Add Affiliation
                        </BButton>
                    </div>

                    <div v-if="author.affiliations.length === 0" class="text-muted small italic py-2">
                        No institutional affiliations specified for this author yet.
                    </div>

                    <div v-for="(affiliation, affiliationIndex) in author.affiliations" :key="affiliationIndex"
                         class="bg-light p-3 rounded mb-2 border">
                        <div class="row g-2 align-items-end">
                            <div class="col-md-5">
                                <label class="form-label fw-semibold small mb-1">Affiliation Name <span class="text-danger">*</span></label>
                                <BFormInput v-model="affiliation.name"
                                            :state="affiliation.nameValid"
                                            placeholder="e.g. University of Freiburg">
                                </BFormInput>
                                <BFormInvalidFeedback>Affiliation name is required.</BFormInvalidFeedback>
                            </div>
                            <div class="col-md-5">
                                <label class="form-label fw-semibold small mb-1 d-flex align-items-center">
                                    ROR ID
                                    <HelpTooltip label="What is a ROR ID?"
                                        text="A ROR ID (Research Organization Registry) is a free, unique identifier for a research institution — the organizational counterpart to an ORCID iD."
                                        link-url="https://ror.org/"
                                        link-text="ror.org"/>
                                </label>
                                <BFormInput v-model="affiliation.rorId"
                                            :state="affiliation.rorIdValid"
                                            placeholder="0xxxxxxxx">
                                </BFormInput>
                                <BFormInvalidFeedback>Must be a valid 9-character ROR ID.</BFormInvalidFeedback>
                            </div>
                            <div class="col-md-2 d-flex justify-content-end gap-1">
                                <BButtonGroup size="sm">
                                    <BButton :disabled="affiliationIndex == 0" @click="moveAffiliationUp(index, affiliationIndex)" variant="outline-secondary" title="Move up">
                                        <i class="fa-solid fa-arrow-up"></i>
                                    </BButton>
                                    <BButton :disabled="affiliationIndex == author.affiliations.length - 1" @click="moveAffiliationDown(index, affiliationIndex)" variant="outline-secondary" title="Move down">
                                        <i class="fa-solid fa-arrow-down"></i>
                                    </BButton>
                                </BButtonGroup>
                                <BButton @click="removeAffiliation(index, affiliationIndex)" variant="outline-danger" size="sm" title="Delete affiliation">
                                    <i class="fa-solid fa-trash-can"></i>
                                </BButton>
                            </div>
                        </div>
                    </div>
                </div>
            </BCard>

            <BButton @click="addAuthor()" variant="outline-primary" class="w-100 py-2 border-dashed">
                <i class="fa-solid fa-plus me-1"></i> Add Another Author
            </BButton>
        </div>

        <div class="d-flex justify-content-between pt-3 border-top">
            <BButton @click="$emit('back')" variant="outline-secondary" size="lg" class="px-4">
                <i class="fa-solid fa-arrow-left me-2"></i> Back
            </BButton>
            <BButton @click="nextStage()" variant="primary" size="lg" class="px-4">
                Continue to License <i class="fa-solid fa-arrow-right ms-2"></i>
            </BButton>
        </div>
    </div>
</template>

<style scoped>
.border-dashed {
    border-style: dashed !important;
    border-width: 2px !important;
}
</style>
