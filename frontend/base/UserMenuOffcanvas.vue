<script setup>

import { ref } from "vue";

import {
    QMenu,
    QBtn,
    QList,
    QItem,
    QItemSection,
    QSeparator,
    QDialog,
    QCard,
    QCardSection,
    QCardActions,
    ClosePopup
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

// Directive for v-close-popup
const vClosePopup = ClosePopup;

</script>

<template>
    <QMenu v-model="visible" anchor="bottom right" self="top right" :offset="[0, 8]">
        <div class="user-menu">
            <div class="user-menu-header">
                <q-icon name="account_circle" size="2rem" />
                <div class="user-info">
                    <div class="user-name">{{ name }}</div>
                    <a v-if="orcid" :href="`https://orcid.org/${orcid}`" class="user-orcid">
                        <img src="/static/images/ORCID-iD_icon_vector.svg" alt="ORCID" height="16" />
                        {{ orcid }}
                    </a>
                </div>
            </div>

            <QSeparator />

            <QList v-if="isStaff" dense>
                <QItem clickable v-close-popup :href="adminUrl">
                    <QItemSection avatar>
                        <q-icon name="settings" />
                    </QItemSection>
                    <QItemSection>Admin interface</QItemSection>
                </QItem>
                <QItem clickable v-close-popup href="/watchman/dashboard/">
                    <QItemSection avatar>
                        <q-icon name="visibility" />
                    </QItemSection>
                    <QItemSection>Watchman dashboard</QItemSection>
                </QItem>
            </QList>

            <QSeparator v-if="isStaff" />

            <QList dense>
                <QItem clickable v-close-popup href="/termsandconditions/">
                    <QItemSection avatar>
                        <q-icon name="description" />
                    </QItemSection>
                    <QItemSection>Terms &amp; conditions</QItemSection>
                </QItem>
                <QItem clickable v-close-popup href="https://github.com/ContactEngineering/TopoBank/discussions">
                    <QItemSection avatar>
                        <q-icon name="forum" />
                    </QItemSection>
                    <QItemSection>Feedback</QItemSection>
                </QItem>
                <QItem clickable v-close-popup @click="contactModal = true">
                    <QItemSection avatar>
                        <q-icon name="mail" />
                    </QItemSection>
                    <QItemSection>Contact</QItemSection>
                </QItem>
                <QItem clickable v-close-popup href="https://doi.org/10.1088/2051-672X/ac860a">
                    <QItemSection avatar>
                        <q-icon name="menu_book" />
                    </QItemSection>
                    <QItemSection>Read our paper!</QItemSection>
                </QItem>
            </QList>

            <QSeparator />

            <div class="user-menu-footer">
                <QBtn
                    color="primary"
                    label="Sign out"
                    @click="signoutModal = true"
                    unelevated
                    class="full-width"
                />
                <VersionInformation class="q-mt-sm" />
            </div>
        </div>
    </QMenu>

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

<style scoped>
.user-menu {
    min-width: 280px;
    background-color: var(--md-sys-color-surface);
}

.user-menu-header {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 16px;
    background-color: var(--md-sys-color-primary-container);
    color: var(--md-sys-color-on-primary-container);
}

.user-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.user-name {
    font-size: var(--md-sys-typescale-title-medium-size);
    font-weight: 500;
}

.user-orcid {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: var(--md-sys-typescale-body-small-size);
    color: var(--md-sys-color-on-primary-container);
    text-decoration: none;
}

.user-orcid:hover {
    text-decoration: underline;
}

.user-menu-footer {
    padding: 16px;
}
</style>
