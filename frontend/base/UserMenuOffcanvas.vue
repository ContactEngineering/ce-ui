<script setup>

import {BModal, BNavbarNav, BNavItem, BOffcanvas} from "bootstrap-vue-next";

import VersionInformation from "topobank/base/VersionInformation.vue";
import {ref} from "vue";

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
    <BOffcanvas v-model="visible" placement="end" footer-class="offcanvas-header">
        <template #title>
            <i class="fa fa-user-circle fa-fw" aria-hidden="true"></i>
            <span class="ms-2">{{ name }}</span>
        </template>

        <template #footer>
            <BNavbarNav class="justify-content-end flex-grow-1 pe-3 mb-3">
                <BNavItem :href="`https://orcid.org/${orcid}`"
                          class="align-self-center">
                    <img src="/static/images/ORCID-iD_icon_vector.svg"
                         alt="ORCID iD icon"/>
                    {{ orcid }}
                </BNavItem>
                <BNavItem class="btn btn-secondary" @click="signoutModal = true">
                    Sign out
                </BNavItem>
                <BNavItem>
                    <VersionInformation></VersionInformation>
                </BNavItem>
            </BNavbarNav>
        </template>

        <BNavbarNav v-if="isStaff" class="justify-content-end flex-grow-1 pe-3 mb-3">
            <BNavItem :href="adminUrl">Admin interface</BNavItem>
            <BNavItem href="/watchman/dashboard/">Watchman dashboard</BNavItem>
            <BNavItem href="/watchman/">Watchman status (JSON)</BNavItem>
        </BNavbarNav>
        <BNavbarNav class="justify-content-end flex-grow-1 pe-3 mb-3">
            <BNavItem href="/termsandconditions/">Terms &amp; conditions</BNavItem>
            <BNavItem href="/help/">Help</BNavItem>
            <BNavItem href="https://github.com/ContactEngineering/TopoBank/discussions">
                Feedback
            </BNavItem>
            <BNavItem @click="contactModal = true">Contact</BNavItem>
            <BNavItem href="https://doi.org/10.1088/2051-672X/ac860a">Read our paper!
            </BNavItem>
        </BNavbarNav>
    </BOffcanvas>

    <!-- Sign out modal-->
    <BModal v-model="signoutModal" title="Ready to leave?">
        <template #ok>
            <a class="btn btn-primary" href="/accounts/logout/">Sign out</a>
        </template>

        Select "Sign out" below if you are ready to end your current session.
    </BModal>

    <!-- Contact modal-->
    <BModal v-model="contactModal" title="Contact" :ok-only="true">
        <p>Is <em>contact.engineering</em> helpful for your research?
        </p>
        <p>We would like to hear from you. Please contact us, if you
            have
            any
            comments, suggestions, or bug
            reports!</p>
        <div>
            <ul>
                <li>Participate at <a
                    href="https://github.com/ComputationalMechanics/TopoBank/discussions"
                    target="_blank">discussions
                    on GitHub</a>, or
                </li>
                <li>open an <a
                    href="https://github.com/ComputationalMechanics/TopoBank/issues"
                    target="_blank">issue
                    on
                    GitHub</a>, or
                </li>
                <li>drop us an <a
                    href="mailto:support@contact.engineering">email</a>.
                </li>
            </ul>
        </div>
        <p>Thank you! The <em>contact.engineering</em> development team.
        </p>
        <p translate="no">
            <em>
                <a href="https://pastewka.org/" target="_blank">Simulation
                    Group</a><br>
                Department of Microsystems Engineering (IMTEK)<br>
                University of Freiburg<br>
                Georges-Köhler-Allee 103<br>
                79110 Freiburg<br>
                Germany<br>
            </em>
        </p>
    </BModal>
</template>