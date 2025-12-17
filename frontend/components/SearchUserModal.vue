<script setup lang="ts">

// NOTE: This component uses axios directly because the user search API endpoint
// (/users/api/user/?name=...&max=...) is not in the OpenAPI schema.
// The schema only has /users/v1/user/ with limit/offset params, not name search.
// Consider updating the backend OpenAPI schema to include this endpoint.
import axios from "axios";
import { ref, watch } from "vue";
import {
    QDialog,
    QCard,
    QCardSection,
    QCardActions,
    QBtn,
    QBtnGroup,
    QInput
} from 'quasar';

const props = defineProps({
    url: {
        type: String,
        default: '/users/api/user/'
    },
    maxResults: {
        type: Number,
        default: 5
    }
});

const emit = defineEmits(['user-selected']);

const showModal = defineModel<boolean>({ default: false });

const _searchTerm = ref('');
const _searchResult = ref([]);

function searchUser(searchTerm: string) {
    axios.get(`${props.url}?name=${searchTerm}&max=${props.maxResults}`).then(response => {
        _searchResult.value = response.data;
    });
}

function selectUser(user: any) {
    emit('user-selected', user);
    showModal.value = false;
}

watch(_searchTerm, (newValue, oldValue) => {
    searchUser(newValue);
});

</script>

<template>
    <QDialog v-model="showModal">
        <QCard style="min-width: 400px;">
            <QCardSection>
                <div class="text-h6">Search user</div>
            </QCardSection>

            <QCardSection>
                <QInput
                    v-model="_searchTerm"
                    label="Name"
                    hint="Search by full name of the user."
                    placeholder="Type to search..."
                    outlined
                    dense
                />
            </QCardSection>

            <QCardSection class="q-pt-none">
                <QBtnGroup vertical class="full-width">
                    <QBtn
                        v-for="user in _searchResult"
                        :key="user.id"
                        outline
                        color="grey"
                        @click="selectUser(user)"
                        class="text-left"
                    >
                        {{ user.name }} ({{ user.orcid }})
                    </QBtn>
                </QBtnGroup>
            </QCardSection>

            <QCardActions align="right">
                <QBtn flat label="Close" v-close-popup />
            </QCardActions>
        </QCard>
    </QDialog>
</template>
