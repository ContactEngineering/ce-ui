<script setup lang="ts">

import { computed, onMounted, ref } from "vue";

import axios from "axios";
import { subjectsToBase64 } from "topobank/utils/api";

import {
    BBadge,
    BButton,
    BButtonGroup,
    BFormCheckbox,
    BListGroupItem
} from "bootstrap-vue-next";

import ThumbnailRow from "./ThumbnailRow.vue";

const selected = defineModel<string[]>("selected");

const props = defineProps({
    dataset: Object
});

const _creator = ref(null);
const _publication = ref(null);

onMounted(() => {
    axios.get(props.dataset.creator)
        .then(response => {
            _creator.value = response.data.name;
        });
    if (props.dataset?.publication) {
        axios.get(props.dataset.publication).then(response => {
            _publication.value = response.data;
        });
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

</script>

<template>
    <BListGroupItem>
        <div class="d-flex">
            <div>
                <BFormCheckbox v-model="selected" :value="dataset.id"></BFormCheckbox>
            </div>
            <div class="flex-grow-1 ms-2 me-2">
                <img v-if="_publication != null"
                     class="float-end ms-2 me-2"
                     variant="dark"
                     :src="`/static/images/cc/${_publication.license}.svg`"
                     title="Dataset can be reused under the terms of a Creative Commons license.">
                <BBadge v-if="_publication != null"
                        class="float-end me-2"
                        :href="`https://doi.org/${_publication.doi_name}`">
                    https://doi.org/{{ _publication.doi_name }}
                </BBadge>
                <a v-if="dataset.publication_doi != null"
                   class="badge bg-dark me-1 text-decoration-none"
                   :href="dataset.publication_doi">{{ dataset.publication_doi }}</a>
                <img v-if="dataset.publication_license != null"
                     :src="`/static/images/cc/${dataset.publication_license}.svg`"
                     title="Dataset can be reused under the terms of a Creative Commons license."
                     style="float:right">
                <p v-if="dataset.sharing_status === 'own'" class='badge bg-info me-1'>
                    Created by you
                </p>
                <p v-if="dataset.sharing_status === 'shared' && _creator == null"
                   class='badge bg-info me-1'>
                    Shared with you
                </p>
                <p v-if="dataset.sharing_status === 'shared' && _creator != null"
                   class='badge bg-info me-1'>
                    Created by {{ _creator }} and shared with you
                </p>
                <p v-for="tag of dataset.tags" class='badge bg-success me-1'>
                    {{ tag }}
                </p>
                <p class="dataset-title">
                    <i class="fa fa-layer-group"></i> {{ dataset.name }}
                </p>
                <p v-if="_publication != null" class="dataset-authors">
                    This digital surface twin was published by {{ publicationAuthorsPretty }} on {{ publicationDatePretty }}
                </p>
                <ThumbnailRow class="mb-3"
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
            <div class="d-block">
                <BButtonGroup vertical size="sm">
                    <BButton variant="light"
                             :href="`/ui/dataset-detail/${ dataset.id }/`">
                        View
                    </BButton>
                    <BButton variant="light"
                             :href="`/ui/analysis-list/?subjects=${subjectsToBase64({surface: [dataset.id]})}`">
                        Analyze
                    </BButton>
                    <BButton variant="light"
                             :href="dataset.api.download">
                        Download
                    </BButton>
                </BButtonGroup>
            </div>
        </div>
    </BListGroupItem>
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