<script setup>

import {onMounted, ref} from "vue";
import {
    BButton,
    BFormInput,
    BModal,
    BNavbar,
    BNavbarBrand,
    BNavbarNav,
    BNavItem,
    BToastOrchestrator,
    useToastController
} from "bootstrap-vue-next";

import NotificationButton from "topobank/base/NotificationButton.vue";
import UserMenuButton from "topobank/base/UserMenuButton.vue";

const {show} = useToastController();

const props = defineProps({
    isAnonymous: Boolean,
    apiUrl: String,
    loginUrl: String,
    adminUrl: String,
    selectUrl: String,
    userName: String,
    name: String,
    orcid: String,
    isStaff: Boolean,
    messages: {
        type: Array,
        default: []
    }
});

const searchInfoModal = ref(false);

const levelToVariant = {
    'error': 'danger',
    'warning': 'warning',
    'info': 'info',
    'success': 'success'
};

const levelToTitle = {
    'error': 'Error',
    'warning': 'Warning',
    'info': 'Information',
    'success': 'Success'
}

onMounted(() => {
    for (const message of props.messages) {
        show?.({
            props: {
                title: levelToTitle[message.level],
                body: message.message,
                variant: levelToVariant[message.level]
            }
        });
    }
});

</script>

<template>
    <BToastOrchestrator/>
    <BNavbar variant="dark" class="navbar-dark">
        <BNavbarBrand href="/" class="d-flex flex-grow-1">
            <img src="/static/images/ce_logo.svg" height="25px">
            &nbsp contact.engineering
        </BNavbarBrand>
        <BNavbarNav>
            <form :action="selectUrl" method="get" class="d-flex">
                <label class="col-form-label visually-hidden"
                       for="inline-form-input-name">Search term</label>
                <BFormInput type="search"
                            name="search"
                            placeholder="Enter search expression">
                </BFormInput>
                <BButton class="ms-1"
                         variant="outline-secondary"
                         type="submit">
                    <i class="fa fa-search" aria-hidden="true"></i>
                </BButton>
                <BButton class="ms-1 me-5"
                         variant="outline-secondary"
                         title="Tips for searching"
                         @click="searchInfoModal = true">
                    <i class="fa fa-info-circle" aria-hidden="true"></i>
                </BButton>
            </form>
        </BNavbarNav>
        <BNavbarNav v-if="isAnonymous">
            <BNavItem>
                <BButton :href="loginUrl" variant="outline-secondary">
                    Sign in
                </BButton>
            </BNavItem>
        </BNavbarNav>
        <NotificationButton v-if="!isAnonymous"></NotificationButton>
        <UserMenuButton
            v-if="!isAnonymous"
            :api-url="apiUrl"
            :admin-url="adminUrl"
            :name="name"
            :orcid="orcid"
            :is-staff="isStaff"
        ></UserMenuButton>
    </BNavbar>

    <!-- Search Help Modal-->
    <BModal title="Tips for searching"
            v-model="searchInfoModal"
            size="xl"
            :ok-only="true">
        <p>Searching is performed over these fields:</p>
        <ul>
            <li>Names of surface and measurements</li>
            <li>Names of tags</li>
            <li>Descriptions of digital surface twins and measurements</li>
        </ul>

        <p>All texts in the search field is split into a list of tokens.
            Searching finds matches
            of the search expression among these tokens. You can build
            search
            expression from search terms
            as follows:</p>

        <table class="table table-bordered table-condensed">
            <thead class="thead-light">
            <tr>
                <th>Search result should list items with</th>
                <th>Search expression</th>
                <th>Comment</th>
            </tr>
            </thead>
            <tbody>
            <tr>
                <td>both <em>AFM</em> and <em>surface</em></td>
                <td><input type="text" value="AFM surface" size="40"
                           readonly>
                </td>
                <td>text not inside quote marks will be interpreted as AND
                </td>
            </tr>
            <tr>
                <td>either <em>AFM</em> or <em>surface</em> or both</td>
                <td><input type="text" value="AFM OR surface" size="40"
                           readonly></td>
                <td>logical OR, least precedence</td>
            </tr>
            <tr>
                <td><em>AFM</em> but not <em>surface</em></td>
                <td><input type="text" value="AFM -surface" size="40"
                           readonly>
                </td>
                <td>the logical not operator is written by using -, has
                    highest
                    precedence
                </td>
            </tr>
            <tr>
                <td>the phrase <em>AFM Surface</em></td>
                <td><input type="text" value='"AFM surface"' size="40"
                           readonly>
                </td>
                <td><em>AFM</em> and <em>surface</em> are found if next to
                    each
                    other
                </td>
            </tr>
            <tr>
                <td><em>AFM Surface</em> as a phrase and <em>imported</em>
                    somewhere else
                </td>
                <td><input type="text" value='"AFM surface" imported'
                           size="40"
                           readonly></td>
                <td></td>
            </tr>
            <tr>
                <td><em>AFM Surface</em> as a phrase and <em>imported</em>
                    but
                    not <em>material</em></td>
                <td><input type="text"
                           value='"AFM surface" imported -material'
                           size="40" readonly></td>
                <td>The above can also be combined. Parentheses are not
                    allowed,
                    all entries
                    are valid search expressions.
                </td>
            </tr>
            </tbody>

        </table>
    </BModal>
</template>