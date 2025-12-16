<script setup>

import { ref } from "vue";

import {
    QDrawer,
    QToolbar,
    QToolbarTitle,
    QBtn,
    QList,
    QItem,
    QItemSection,
    QSeparator,
    QDialog,
    QCard,
    QCardSection,
    QCardActions,
    QSpace
} from "quasar";

import VersionInformation from "./VersionInformation.vue";

const visible = defineModel("visible");

const props = defineProps({
    apiUrl: String,
    adminUrl: String,
    name: String,
    orcid: String,
    isStaff: Boolean
});

const signoutModal = ref(false);
const contactModal = ref(false);

</script>

<template>
    <QDrawer v-model="visible" side="right" :width="300" bordered overlay>
        <div class="column full-height">
            <QToolbar class="bg-primary text-white">
                <i class="fa fa-user-circle fa-fw q-mr-sm" aria-hidden="true"></i>
                <QToolbarTitle>{{ name }}</QToolbarTitle>
                <QBtn flat round icon="close" @click="visible = false" />
            </QToolbar>

            <div class="col">
                <QList v-if="isStaff">
                    <QItem clickable :href="adminUrl">
                        <QItemSection>Admin interface</QItemSection>
                    </QItem>
                    <QItem clickable href="/watchman/dashboard/">
                        <QItemSection>Watchman dashboard</QItemSection>
                    </QItem>
                    <QItem clickable href="/watchman/">
                        <QItemSection>Watchman status (JSON)</QItemSection>
                    </QItem>
                </QList>
                <QSeparator v-if="isStaff" />
                <QList>
                    <QItem clickable href="/termsandconditions/">
                        <QItemSection>Terms &amp; conditions</QItemSection>
                    </QItem>
                    <QItem clickable href="https://github.com/ContactEngineering/TopoBank/discussions">
                        <QItemSection>Feedback</QItemSection>
                    </QItem>
                    <QItem clickable @click="contactModal = true">
                        <QItemSection>Contact</QItemSection>
                    </QItem>
                    <QItem clickable href="https://doi.org/10.1088/2051-672X/ac860a">
                        <QItemSection>Read our paper!</QItemSection>
                    </QItem>
                </QList>
            </div>

            <QSeparator />
            <div class="q-pa-md">
                <div class="q-mb-sm">
                    <a :href="`https://orcid.org/${orcid}`" class="flex items-center">
                        <img src="/static/images/ORCID-iD_icon_vector.svg" alt="ORCID iD icon" class="q-mr-sm" />
                        {{ orcid }}
                    </a>
                </div>
                <QBtn color="secondary" label="Sign out" @click="signoutModal = true" class="full-width q-mb-sm" />
                <VersionInformation />
            </div>
        </div>
    </QDrawer>

    <!-- Sign out modal-->
    <QDialog v-model="signoutModal">
        <QCard style="min-width: 350px">
            <QCardSection>
                <div class="text-h6">Ready to leave?</div>
            </QCardSection>
            <QCardSection>
                Select "Sign out" below if you are ready to end your current session.
            </QCardSection>
            <QCardActions align="right">
                <QBtn flat label="Cancel" v-close-popup />
                <QBtn color="primary" label="Sign out" href="/accounts/logout/" />
            </QCardActions>
        </QCard>
    </QDialog>

    <!-- Contact modal-->
    <QDialog v-model="contactModal">
        <QCard style="min-width: 400px">
            <QCardSection>
                <div class="text-h6">Contact</div>
            </QCardSection>
            <QCardSection>
                <p>Is <em>contact.engineering</em> helpful for your research?</p>
                <p>We would like to hear from you. Please contact us, if you have any comments, suggestions, or bug reports!</p>
                <ul>
                    <li>Participate at <a href="https://github.com/ComputationalMechanics/TopoBank/discussions" target="_blank">discussions on GitHub</a>, or</li>
                    <li>open an <a href="https://github.com/ComputationalMechanics/TopoBank/issues" target="_blank">issue on GitHub</a>, or</li>
                    <li>drop us an <a href="mailto:support@contact.engineering">email</a>.</li>
                </ul>
                <p>Thank you! The <em>contact.engineering</em> development team.</p>
                <p translate="no">
                    <em>
                        <a href="https://pastewka.org/" target="_blank">Simulation Group</a><br>
                        Department of Microsystems Engineering (IMTEK)<br>
                        University of Freiburg<br>
                        Georges-Köhler-Allee 103<br>
                        79110 Freiburg<br>
                        Germany<br>
                    </em>
                </p>
            </QCardSection>
            <QCardActions align="right">
                <QBtn flat label="Close" v-close-popup />
            </QCardActions>
        </QCard>
    </QDialog>
</template>