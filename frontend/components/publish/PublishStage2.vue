<script setup lang="ts">

import { computed, inject, ref } from "vue";
import { BCard, BButton, BButtonGroup, BFormInput, BAlert } from "bootstrap-vue-next";

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

const appProps = inject("appProps");

const emit = defineEmits(["back", "continue"]);

const authors = ref<Author[]>([emptyAuthor()]);

function fillAuthor(index) {
    authors.value[index].person = {
        firstName: appProps.userFirstName,
        firstNameValid: null,
        lastName: appProps.userLastName,
        lastNameValid: null,
        orcidId: appProps.userOrcid,
        orcidIdValid: null
    };
}

function addAuthor() {
    authors.value.push(emptyAuthor());
}

function addAffiliation(index) {
    authors.value[index].affiliations.push(emptyAffiliation());
}

function removeAuthor(index) {
    authors.value.splice(index, 1);
}

function removeAffiliation(authorIndex, affiliationIndex) {
    if (authorIndex >= 0 && authorIndex < authors.value.length) {
        authors.value[authorIndex].affiliations.splice(affiliationIndex, 1);
    }
}

function moveAuthorUp(index) {
    if (index > 0 && index < authors.value.length) {
        [authors.value[index], authors.value[index - 1]] =
            [authors.value[index - 1], authors.value[index]];
    }
}

function moveAffiliationUp(authorIndex, affiliationIndex) {
    if (authorIndex >= 0 && authorIndex < authors.value.length) {
        const affiliations = authors.value[authorIndex].affiliations;
        if (affiliationIndex > 0 && affiliationIndex < affiliations.length) {
            [affiliations[affiliationIndex], affiliations[affiliationIndex - 1]] =
                [affiliations[affiliationIndex - 1], affiliations[affiliationIndex]];
        }
    }
}

function moveAuthorDown(index) {
    if (index >= 0 && index < authors.value.length - 1) {
        [authors.value[index], authors.value[index + 1]] =
            [authors.value[index + 1], authors.value[index]];
    }
}

function moveAffiliationDown(authorIndex, affiliationIndex) {
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
    <div v-if="props.stage == 1" class="mt-4">
        <h2 class="alert-heading">
            Please enter the authors
        </h2>
        <BAlert :model-value="true" variant="secondary">
            <i class="fa-solid fa-circle-info me-2"></i>Authors will be listed like this: <strong> {{ authorsString }} </strong>
        </BAlert>
        <div class="p-2">
            <BCard v-for="(author, index) in authors" class="mb-2" header-tag="header"
                   footer-tag="footer">
                <template #header>
                    <h5 class="mb-0">{{ index + 1 }}. Author</h5>
                </template>
                <div class="d-flex flex-row justify-content-evenly align-items-end">
                    <BButtonGroup aria-label="Basic example">
                        <BButton v-if="authors.length == 1" disabled variant="danger"
                                 title="Delete this author">
                            <i class="fa-solid fa-trash-can"></i>
                        </BButton>
                        <BButton v-else @click="removeAuthor(index)" variant="danger"
                                 title="Delete this author">
                            <i class="fa-solid fa-trash-can"></i>
                        </BButton>
                        <BButton @click="fillAuthor(index)" variant="info"
                                 title="Insert your name and ORCID ID as author">
                            <i class="fa-solid fa-id-card"></i>
                        </BButton>
                        <BButton v-if="index == 0" disabled>
                            <i class="fa-solid fa-arrow-up"></i>
                        </BButton>
                        <BButton v-else @click="moveAuthorUp(index)" title="Move up">
                            <i class="fa-solid fa-arrow-up"></i>
                        </BButton>
                        <BButton v-if="index == authors.length - 1" disabled>
                            <i class="fa-solid fa-arrow-down"></i>
                        </BButton>
                        <BButton v-else @click="moveAuthorDown(index)"
                                 title="Move down">
                            <i class="fa-solid fa-arrow-down"></i>
                        </BButton>
                    </BButtonGroup>
                    <div class="d-flex flex-column">
                        <span>First name*</span>
                        <BFormInput v-model="author.person.firstName"
                                    :state="author.person.firstNameValid"
                                    aria-describedby="input-live-help input-live-feedback"
                                    placeholder="First name">
                        </BFormInput>
                    </div>
                    <div class="d-flex flex-column">
                        <span>Last name*</span>
                        <BFormInput v-model="author.person.lastName"
                                    :state="author.person.lastNameValid"
                                    placeholder="Last name">
                        </BFormInput>
                    </div>
                    <div class="d-flex flex-column">
                        <span>ORCID iD (optional)
                            <HelpTooltip label="What is an ORCID iD?"
                                text="An ORCID iD is a free, unique identifier for researchers that permanently links you to your work — regardless of name changes or spellings."
                                link-url="https://orcid.org/"
                                link-text="orcid.org"/>
                        </span>
                        <BFormInput v-model="author.person.orcidId"
                                    :state="author.person.orcidIdValid"
                                    placeholder="xxxx-xxxx-xxxx-xxxx">
                        </BFormInput>
                    </div>
                </div>
                <template #footer>
                    <h6 class="mb-0">{{ author.affiliations.length }} Affiliations</h6>
                    <div v-for="(affiliation, affiliationIndex) in author.affiliations"
                         class="d-flex flex-row justify-content-center align-items-end mt-2">
                        <BButtonGroup class="me-2">
                            <BButton
                                @click="removeAffiliation(index, affiliationIndex)"
                                variant="danger"
                                title="Delete this affiliation">
                                <i class="fa-solid fa-trash-can"></i>
                            </BButton>
                            <BButton v-if="affiliationIndex == 0" disabled>
                                <i class="fa-solid fa-arrow-up"></i>
                            </BButton>
                            <BButton v-else
                                     @click="moveAffiliationUp(index, affiliationIndex)">
                                <i class="fa-solid fa-arrow-up"></i>
                            </BButton>
                            <BButton
                                v-if="affiliationIndex == author.affiliations.length - 1"
                                disabled>
                                <i class="fa-solid fa-arrow-down"></i>
                            </BButton>
                            <BButton v-else
                                     @click="moveAffiliationDown(index, affiliationIndex)">
                                <i class="fa-solid fa-arrow-down"></i>
                            </BButton>
                        </BButtonGroup>
                        <div class="d-flex flex-column me-2">
                            <span>Affiliation name*</span>
                            <BFormInput v-model="affiliation.name"
                                        :state="affiliation.nameValid"
                                        placeholder="Name">
                            </BFormInput>
                        </div>
                        <div class="d-flex flex-column">
                            <span>ROR ID (optional)
                                <HelpTooltip label="What is a ROR ID?"
                                    text="A ROR ID (Research Organization Registry) is a free, unique identifier for a research institution — the organizational counterpart to an ORCID iD."
                                    link-url="https://ror.org/"
                                    link-text="ror.org"/>
                            </span>
                            <BFormInput v-model="affiliation.rorId"
                                        :state="affiliation.rorIdValid"
                                        placeholder="0xxxxxxxx">
                            </BFormInput>
                        </div>
                    </div>

                    <BButton @click="addAffiliation(index)" variant="success"
                             class="mt-2">
                        <i class="fa-solid fa-plus"></i>
                        One more affiliation
                    </BButton>
                </template>
            </BCard>

            <BButton @click="addAuthor()" variant="success">
                <i class="fa-solid fa-plus"></i>
                One more author
            </BButton>
        </div>

        <div class="d-flex flex-row justify-content-between">
            <BButton @click="$emit('back')" variant="primary">
                Back
            </BButton>
            <BButton @click="nextStage()" variant="primary">
                Continue
            </BButton>
        </div>
    </div>
</template>
