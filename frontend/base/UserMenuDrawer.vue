<script setup>

import { inject, ref } from "vue";

import {
    QBtn,
    QList,
    QItem,
    QItemSection,
    QSeparator,
    QIcon,
    QToolbar,
    QToolbarTitle,
    QDialog,
    QCard,
    QCardSection,
    QCardActions
} from "quasar";

import VersionInformation from "./VersionInformation.vue";

const appProps = inject("appProps");
const rightDrawer = inject('rightDrawer');

const signoutModal = ref(false);
const contactModal = ref(false);

</script>

<template>
    <div class="column full-height">
        <QToolbar class="bg-primary text-white">
            <QIcon name="account_circle" size="sm" class="q-mr-sm" />
            <QToolbarTitle>Account</QToolbarTitle>
            <QBtn flat round dense icon="close" @click="rightDrawer.close()" />
        </QToolbar>

        <!-- User Info -->
        <div class="q-pa-md bg-grey-2">
            <div class="row items-center q-gutter-sm">
                <QIcon name="account_circle" size="2.5rem" color="primary" />
                <div>
                    <div class="text-subtitle1 text-weight-medium">{{ appProps.userFullName }}</div>
                    <a v-if="appProps.userOrcid" :href="`https://orcid.org/${appProps.userOrcid}`" class="text-caption row items-center q-gutter-xs" target="_blank">
                        <img src="/static/images/ORCID-iD_icon_vector.svg" alt="ORCID" height="14" />
                        <span>{{ appProps.userOrcid }}</span>
                    </a>
                </div>
            </div>
        </div>

        <QSeparator />

        <!-- Admin Links -->
        <QList v-if="appProps.userIsStaff">
            <QItem clickable :href="appProps.adminUrl" @click="rightDrawer.close()">
                <QItemSection avatar>
                    <QIcon name="settings" />
                </QItemSection>
                <QItemSection>Admin interface</QItemSection>
            </QItem>
            <QItem clickable href="/watchman/dashboard/" @click="rightDrawer.close()">
                <QItemSection avatar>
                    <QIcon name="visibility" />
                </QItemSection>
                <QItemSection>Watchman dashboard</QItemSection>
            </QItem>
        </QList>

        <QSeparator v-if="appProps.userIsStaff" />

        <!-- General Links -->
        <QList>
            <QItem clickable href="/termsandconditions/" @click="rightDrawer.close()">
                <QItemSection avatar>
                    <QIcon name="description" />
                </QItemSection>
                <QItemSection>Terms & conditions</QItemSection>
            </QItem>
            <QItem clickable href="https://github.com/ContactEngineering/TopoBank/discussions" target="_blank" @click="rightDrawer.close()">
                <QItemSection avatar>
                    <QIcon name="forum" />
                </QItemSection>
                <QItemSection>Feedback</QItemSection>
            </QItem>
            <QItem clickable @click="contactModal = true">
                <QItemSection avatar>
                    <QIcon name="mail" />
                </QItemSection>
                <QItemSection>Contact</QItemSection>
            </QItem>
            <QItem clickable href="https://doi.org/10.1088/2051-672X/ac860a" target="_blank" @click="rightDrawer.close()">
                <QItemSection avatar>
                    <QIcon name="menu_book" />
                </QItemSection>
                <QItemSection>Read our paper!</QItemSection>
            </QItem>
        </QList>

        <!-- Spacer to push footer to bottom -->
        <div class="col-grow"></div>

        <!-- Sign Out (at bottom) -->
        <QSeparator />
        <div class="q-pa-md">
            <QBtn
                color="primary"
                label="Sign out"
                @click="signoutModal = true"
                unelevated
                class="full-width"
            />
            <VersionInformation class="q-mt-md" />
        </div>
    </div>

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
                        Georges-Kohler-Allee 103<br>
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
