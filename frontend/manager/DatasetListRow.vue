<script setup lang="ts">

import { computed, onMounted, ref } from "vue";

import { getIdFromUrl, subjectsToBase64 } from "topobank/utils/api";
import { usersV1UserRetrieve, goPublicationRetrieve } from "@/api";

import {
    QBadge,
    QBtn,
    QCheckbox,
    QItem
} from "quasar";

import ThumbnailRow from "./ThumbnailRow.vue";

const selected = defineModel<string[]>("selected");

const props = defineProps({
    dataset: Object
});

const _creator = ref(null);
const _publication = ref(null);

onMounted(async () => {
    if (props.dataset.creator) {
        try {
            const userId = getIdFromUrl(props.dataset.creator);
            const response = await usersV1UserRetrieve({path: {id: userId}});
            _creator.value = response.data.name;
        } catch (error) {
            // Ignore error - creator may not exist
        }
    }
    if (props.dataset?.publication) {
        try {
            const publicationId = getIdFromUrl(props.dataset.publication);
            const response = await goPublicationRetrieve({path: {id: publicationId}});
            _publication.value = response.data;
        } catch (error) {
            // Ignore error - publication may not exist
        }
    }
});

const publicationAuthorsPretty = computed(() => {
    if (_publication.value == null) {
        return null;
    }
    return _publication.value.authors_json.map(author => `${author.first_name} ${author.last_name}`).join(", ");
});

const publicationDatePretty = computed(() => {
    return new Date(_publication.value?.datetime).toISOString().substring(0, 10);
});

const creationDatePretty = computed(() => {
    return new Date(props.dataset.creation_datetime).toISOString().substring(0, 10);
});

const isSelected = computed({
    get() {
        return selected.value?.includes(props.dataset.id) ?? false;
    },
    set(value) {
        if (value) {
            if (!selected.value.includes(props.dataset.id)) {
                selected.value = [...selected.value, props.dataset.id];
            }
        } else {
            selected.value = selected.value.filter(id => id !== props.dataset.id);
        }
    }
});

</script>

<template>
    <QItem class="dataset-list-row full-width">
        <div class="row no-wrap full-width">
            <div class="q-mr-sm">
                <QCheckbox v-model="isSelected" />
            </div>
            <div class="col">
                <img v-if="_publication != null"
                     class="float-right q-ml-sm q-mr-sm"
                     :src="`/static/images/cc/${_publication.license}.svg`"
                     title="Dataset can be reused under the terms of a Creative Commons license.">
                <QBadge v-if="_publication != null"
                        class="float-right q-mr-sm cursor-pointer"
                        @click="window.location.href = `https://doi.org/${_publication.doi_name}`">
                    https://doi.org/{{ _publication.doi_name }}
                </QBadge>
                <a v-if="dataset.publication_doi != null"
                   class="badge bg-dark q-mr-xs text-decoration-none"
                   :href="dataset.publication_doi">{{ dataset.publication_doi }}</a>
                <img v-if="dataset.publication_license != null"
                     :src="`/static/images/cc/${dataset.publication_license}.svg`"
                     title="Dataset can be reused under the terms of a Creative Commons license."
                     style="float:right">
                <QBadge v-if="dataset.sharing_status === 'own'" color="info" class="q-mr-xs">
                    Created by you
                </QBadge>
                <QBadge v-if="dataset.sharing_status === 'shared' && _creator == null"
                        color="info" class="q-mr-xs">
                    Shared with you
                </QBadge>
                <QBadge v-if="dataset.sharing_status === 'shared' && _creator != null"
                        color="info" class="q-mr-xs">
                    Created by {{ _creator }} and shared with you
                </QBadge>
                <QBadge v-for="tag of dataset.tags" :key="tag" color="positive" class="q-mr-xs">
                    {{ tag }}
                </QBadge>
                <p class="dataset-title">
                    <q-icon name="layers" /> {{ dataset.name }}
                </p>
                <p v-if="_publication != null" class="dataset-authors">
                    This digital surface twin was published by {{ publicationAuthorsPretty }} on {{ publicationDatePretty }}
                </p>
                <ThumbnailRow class="q-mb-md"
                              :data-source-list-url="dataset.topographies">
                </ThumbnailRow>
                <p v-if="_publication == null" class="dataset-authors">
                    This digital surface twin is unpublished.
                    It was created
                    <span v-if="_creator != null">
                        by {{ _creator }}
                    </span>
                    <span v-if="dataset.creation_datetime != null">
                        on {{ creationDatePretty }}
                    </span>.
                </p>
                <p v-if="dataset.description != null && dataset.description !== ''"
                   class="dataset-description">
                    {{ dataset.description }}</p>
                <p v-if="dataset.topography_count != null && dataset.version != null"
                   class="dataset-info">
                    This is version {{ dataset.version }} of this digital surface twin
                    and
                    contains
                    {{ dataset.topography_count }} measurements.
                </p>
                <p v-else-if="dataset.version != null" class="dataset-info">
                    This is version {{ dataset.version }} of this digital surface twin.
                </p>
                <p v-else-if="dataset.topography_count != null" class="dataset-info">
                    This digital surface twin contains {{ dataset.topography_count }}
                    measurements.
                </p>
            </div>
            <div class="column justify-center q-ml-sm">
                <QBtn flat dense icon="visibility"
                      :href="`/ui/dataset-detail/${ dataset.id }/`"
                      label="View" />
                <QBtn flat dense icon="analytics"
                      :href="`/ui/analysis-list/?subjects=${subjectsToBase64({surface: [dataset.id]})}`"
                      label="Analyze" />
                <QBtn flat dense icon="download"
                      :href="dataset.api.download"
                      label="Download" />
            </div>
        </div>
    </QItem>
</template>

<style scoped>

.dataset-title {
    font-size: medium;
    font-weight: bold;
}

.dataset-authors {
    font-size: medium;
    color: var(--secondary);
}

/* The following cuts the description text after 3 display lines */
.dataset-description {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

</style>