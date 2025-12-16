<script setup lang="ts">

import { computed, inject, ref } from "vue";
import {
    QCard,
    QCardSection,
    QBtn,
    QBtnGroup,
    QInput,
    QBanner
} from "quasar";

const props = defineProps({
    stage: Number
});

const appProps = inject("appProps");

const emit = defineEmits(["back", "continue"]);

interface Person {
    firstName: string;
    firstNameValid: boolean;
    lastName: string;
    lastNameValid: boolean;
    orcidId: string;
    orcidIdValid: boolean;
}

interface Affiliation {
    name: string;
    nameValid: boolean;
    rorId: string;
    rorIdValid: boolean;
}

interface Author {
    person: Person;
    affiliations: Affiliation[];
}

const authors = ref<Author[]>(
    [{
        person: {
            firstName: "",
            firstNameValid: null,
            lastName: "",
            lastNameValid: null,
            orcidId: "",
            orcidIdValid: null
        },
        affiliations: []
    }]);

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
    authors.value.push({
        person:
            {
                firstName: "",
                firstNameValid: null,
                lastName: "",
                lastNameValid: null,
                orcidId: "",
                orcidIdValid: null
            },
        affiliations: []
    });
}

function addAffiliation(index) {
    authors.value[index].affiliations.push(
        {
            name: "",
            nameValid: null,
            rorId: "",
            rorIdValid: null
        }
    );
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

const orcidIdRegex = new RegExp("^(\\d{4}-){3}\\d{3}(\\d|X)$");
const rorIdRegex = new RegExp("^0[a-z|0-9]{6}[0-9]{2}$");

function checkValidity() {
    authors.value.forEach(author => {
        author.person.firstNameValid = author.person.firstName != "";
        author.person.lastNameValid = author.person.lastName != "";
        author.person.orcidIdValid =
            author.person.orcidId === "" || orcidIdRegex.test(author.person.orcidId);
        author.affiliations.forEach(affiliation => {
            affiliation.nameValid = affiliation.name != "";
            affiliation.rorIdValid =
                affiliation.rorId === "" || rorIdRegex.test(affiliation.rorId);
        });
    });
    return authors.value.every(x =>
        x.person.firstNameValid &&
        x.person.lastNameValid &&
        x.person.orcidIdValid &&
        x.affiliations.every(y => y.nameValid && y.rorIdValid));
}

function nextStage() {
    if (!checkValidity()) {
        return;
    }
    emit("continue", authors.value);
}

const authorsString = computed(() => {
    return authors.value.map((author) => `${author.person.firstName} ${author.person.lastName}`).join(", ");
});

</script>
<template>
    <div v-if="props.stage == 1" class="q-mt-md">
        <h2 class="alert-heading">
            Please enter the authors
        </h2>
        <QBanner class="bg-info text-white q-mb-md">
            Authors will be listed like this: <strong> {{ authorsString }} </strong>
        </QBanner>
        <div class="q-pa-sm">
            <QCard v-for="(author, index) in authors" :key="index" class="q-mb-sm">
                <QCardSection class="bg-grey-3">
                    <h5 class="q-ma-none">{{ index + 1 }}. Author</h5>
                </QCardSection>
                <QCardSection>
                    <div class="flex row justify-evenly items-end">
                        <QBtnGroup flat>
                            <QBtn v-if="authors.length == 1" disable color="negative"
                                 title="Delete this author">
                                <i class="fa-solid fa-trash-can"></i>
                            </QBtn>
                            <QBtn v-else @click="removeAuthor(index)" color="negative"
                                 title="Delete this author">
                                <i class="fa-solid fa-trash-can"></i>
                            </QBtn>
                            <QBtn @click="fillAuthor(index)" color="info"
                                 title="Insert your name and ORCID ID as author">
                                <i class="fa-solid fa-id-card"></i>
                            </QBtn>
                            <QBtn v-if="index == 0" disable flat>
                                <i class="fa-solid fa-arrow-up"></i>
                            </QBtn>
                            <QBtn v-else @click="moveAuthorUp(index)" flat title="Move up">
                                <i class="fa-solid fa-arrow-up"></i>
                            </QBtn>
                            <QBtn v-if="index == authors.length - 1" disable flat>
                                <i class="fa-solid fa-arrow-down"></i>
                            </QBtn>
                            <QBtn v-else @click="moveAuthorDown(index)" flat
                                 title="Move down">
                                <i class="fa-solid fa-arrow-down"></i>
                            </QBtn>
                        </QBtnGroup>
                        <div class="flex column">
                            <span>First name*</span>
                            <QInput v-model="author.person.firstName"
                                    :error="author.person.firstNameValid === false"
                                    error-message="First name is required"
                                    placeholder="First name"
                                    dense
                                    outlined>
                            </QInput>
                        </div>
                        <div class="flex column">
                            <span>Last name*</span>
                            <QInput v-model="author.person.lastName"
                                    :error="author.person.lastNameValid === false"
                                    error-message="Last name is required"
                                    placeholder="Last name"
                                    dense
                                    outlined>
                            </QInput>
                        </div>
                        <div class="flex column">
                            <span>ORCID ID (optional)</span>
                            <QInput v-model="author.person.orcidId"
                                    :error="author.person.orcidIdValid === false"
                                    error-message="Invalid ORCID ID format"
                                    placeholder="xxxx-xxxx-xxxx-xxxx"
                                    dense
                                    outlined>
                            </QInput>
                        </div>
                    </div>
                </QCardSection>
                <QCardSection class="bg-grey-2">
                    <h6 class="q-ma-none q-mb-sm">{{ author.affiliations.length }} Affiliations</h6>
                    <div v-for="(affiliation, affiliationIndex) in author.affiliations"
                         :key="affiliationIndex"
                         class="flex row justify-center items-end q-mt-sm">
                        <QBtnGroup class="q-mr-sm" flat>
                            <QBtn
                                @click="removeAffiliation(index, affiliationIndex)"
                                color="negative"
                                title="Delete this affiliation">
                                <i class="fa-solid fa-trash-can"></i>
                            </QBtn>
                            <QBtn v-if="affiliationIndex == 0" disable flat>
                                <i class="fa-solid fa-arrow-up"></i>
                            </QBtn>
                            <QBtn v-else
                                 @click="moveAffiliationUp(index, affiliationIndex)" flat>
                                <i class="fa-solid fa-arrow-up"></i>
                            </QBtn>
                            <QBtn
                                v-if="affiliationIndex == author.affiliations.length - 1"
                                disable flat>
                                <i class="fa-solid fa-arrow-down"></i>
                            </QBtn>
                            <QBtn v-else
                                 @click="moveAffiliationDown(index, affiliationIndex)" flat>
                                <i class="fa-solid fa-arrow-down"></i>
                            </QBtn>
                        </QBtnGroup>
                        <div class="flex column q-mr-sm">
                            <span>Affiliation name*</span>
                            <QInput v-model="affiliation.name"
                                    :error="affiliation.nameValid === false"
                                    error-message="Affiliation name is required"
                                    placeholder="Name"
                                    dense
                                    outlined>
                            </QInput>
                        </div>
                        <div class="flex column">
                            <span>ROR ID (optional)</span>
                            <QInput v-model="affiliation.rorId"
                                    :error="affiliation.rorIdValid === false"
                                    error-message="Invalid ROR ID format"
                                    placeholder="0xxxxxxxx"
                                    dense
                                    outlined>
                            </QInput>
                        </div>
                    </div>

                    <QBtn @click="addAffiliation(index)" color="positive"
                         class="q-mt-sm">
                        <i class="fa-solid fa-plus q-mr-xs"></i>
                        One more affiliation
                    </QBtn>
                </QCardSection>
            </QCard>

            <QBtn @click="addAuthor()" color="positive">
                <i class="fa-solid fa-plus q-mr-xs"></i>
                One more author
            </QBtn>
        </div>

        <div class="flex row justify-between q-mt-md">
            <QBtn @click="$emit('back')" color="primary">
                Back
            </QBtn>
            <QBtn @click="nextStage()" color="primary">
                Continue
            </QBtn>
        </div>
    </div>
</template>
