<script setup lang="ts">

import { computed, ref } from "vue";

import axios from "axios";
import { getIdFromUrl, subjectsToBase64 } from "@/utils/api";
import { describeVersions } from "@/utils/versions";

import {
    BBadge,
    BButton,
    BButtonGroup,
    BFormCheckbox,
    BListGroupItem
} from "bootstrap-vue-next";

import ThumbnailRow from "@/components/manager/ThumbnailRow.vue";
import DownloadModal from "@/components/ui/DownloadModal.vue";

const selected = defineModel<string[]>("selected");

const props = defineProps({
    dataset: Object
});

/* The v2 list response embeds the creator's name and a publication summary,
   so a row makes no requests of its own. */
const _creator = computed(() => props.dataset?.created_by?.name ?? null);
const _publication = computed(() => props.dataset?.publication ?? null);
const _downloadModal = ref(null);

/* Older versions of this dataset. The list shows only the latest version, so the
   others have to be reachable from here; they are fetched when the row is
   expanded rather than for every row of every page. */
const _versionsVisible = ref(false);
const _versions = ref(null);
const _versionsLoading = ref(false);

/* Download this dataset as a ZIP archive. A published dataset has an archived container that can be fetched straight
   away; everything else is assembled by a Celery worker, with the modal reporting progress. See `DatasetDetail`. */
function download() {
    const archivedContainer = _publication.value?.download_url;
    if (archivedContainer != null) {
        window.location.assign(archivedContainer);
        return;
    }
    _downloadModal.value.download(
        props.dataset.api.async_download,
        {title: `Download '${props.dataset.name}'`});
}

const versions = computed(() => {
    return describeVersions(_versions.value, props.dataset?.version);
});

function toggleVersions() {
    _versionsVisible.value = !_versionsVisible.value;
    if (!_versionsVisible.value || _versions.value != null || _versionsLoading.value) {
        return;
    }
    /* All versions of a dataset share an original, which is what the publication
       endpoint groups by. */
    const originalSurface = _publication.value?.original_surface;
    if (originalSurface == null) {
        _versions.value = [];
        return;
    }
    _versionsLoading.value = true;
    axios.get(`/go/publication/?original_surface=${getIdFromUrl(originalSurface)}`)
        .then(response => {
            _versions.value = response.data.results ?? response.data;
        })
        .catch(() => {
            // Leave the list empty; the row itself stays usable
            _versions.value = [];
        })
        .finally(() => {
            _versionsLoading.value = false;
        });
}

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
    return new Date(props.dataset.created_at).toISOString().substring(0, 10);
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
                              :data-sources="dataset.topographies">
                </ThumbnailRow>
                <p v-if="_publication == null" class="dataset-authors">
                    This digital surface twin is unpublished.
                    It was created
                    <span v-if="_creator != null">
                        by {{ _creator }}
                    </span>
                    <span v-if="dataset.created_at != null">
                        on {{ creationDatePretty }}
                    </span>.
                </p>
                <p v-if="dataset.description != null && dataset.description !== ''"
                   class="dataset-description">
                    {{ dataset.description }}</p>
                <p v-if="dataset.topographies != null" class="dataset-info">
                    This digital surface twin contains
                    {{ dataset.topographies.length }} measurements.
                </p>
                <!-- The list shows only the latest version of a dataset, so say
                     which one this is and offer the others. -->
                <div v-if="dataset.version != null" class="dataset-info">
                    <BBadge variant="secondary">Version {{ dataset.version }}</BBadge>
                    <BButton v-if="dataset.nb_versions > 1"
                             class="ms-2 py-0"
                             size="sm"
                             variant="outline-secondary"
                             @click="toggleVersions">
                        <i :class="_versionsVisible ? 'fa fa-caret-up' : 'fa fa-caret-down'"
                           class="me-1"></i>{{ dataset.nb_versions }} versions
                    </BButton>
                    <div v-if="_versionsVisible" class="mt-1 ms-1">
                        <span v-if="_versionsLoading">Loading versions&hellip;</span>
                        <span v-else-if="versions.length === 0">
                            The other versions of this dataset are not available.
                        </span>
                        <ul v-else class="list-unstyled mb-0">
                            <li v-for="version of versions" :key="version.version">
                                <a :href="version.href">Version {{ version.version }}</a>
                                <span v-if="version.date"> &mdash; {{ version.date }}</span>
                                <span v-if="version.isCurrent" class="text-secondary"> (shown here)</span>
                            </li>
                        </ul>
                    </div>
                </div>
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
                             @click="download()">
                        Download
                    </BButton>
                </BButtonGroup>
            </div>
        </div>
        <DownloadModal ref="_downloadModal"></DownloadModal>
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