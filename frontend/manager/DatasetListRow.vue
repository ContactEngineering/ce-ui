<script setup>

import {computed, onMounted, ref} from "vue";

import {
    BButton,
    BButtonGroup,
    BFormCheckbox,
    BListGroupItem
} from "bootstrap-vue-next";

import ThumbnailRow from "./ThumbnailRow.vue";
import axios from "axios";
import {subjectsToBase64} from "topobank/utils/api";

const props = defineProps({
    dataset: Object
});

const _creator = ref(null);

onMounted(() => {
    axios.get(props.dataset.creator)
        .then(response => {
            _creator.value = response.data.name;
        });
});

const publicationDatePretty = computed(() => {
    return new Date(props.dataset.publication_date).toISOString().substring(0, 10);
});

const creationDatePretty = computed(() => {
    return new Date(props.dataset.creation_datetime).toISOString().substring(0, 10);
});

</script>

<template>
    <BListGroupItem>
        <div class="d-flex">
            <div>
                <BFormCheckbox></BFormCheckbox>
            </div>
            <div class="flex-grow-1 ms-2 me-2">
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
                <ThumbnailRow class="mb-3"
                              :data-source-list-url="dataset.topographies">
                </ThumbnailRow>
                <p v-if="dataset.publication_authors != null" class="dataset-authors">
                    {{ dataset.publication_authors }}
                    (published {{ publicationDatePretty }})
                </p>
                <p v-else class="dataset-authors">
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
                    <BButton variant="outline-secondary"
                             :href="`/ui/html/surface/?surface=${ dataset.id }`">
                        View
                    </BButton>
                    <BButton variant="outline-secondary"
                             :href="`/ui/html/analysis-list/?subjects=${subjectsToBase64({surface: [dataset.id]})}`">
                        Analyze
                    </BButton>
                    <BButton variant="outline-secondary"
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