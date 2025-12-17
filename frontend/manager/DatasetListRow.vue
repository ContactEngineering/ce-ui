<script setup lang="ts">

import { computed, onMounted, ref } from "vue";

import { getIdFromUrl, subjectsToBase64 } from "topobank/utils/api";
import { usersV1UserRetrieve, goPublicationRetrieve } from "@/api";

import {
    QBadge,
    QBtn,
    QCheckbox,
    QIcon,
    QItem,
    QItemSection
} from "quasar";

import ThumbnailRow from "./ThumbnailRow.vue";

const selected = defineModel<string[]>("selected");
const _isHovered = ref(false);

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
    <QItem class="dataset-list-row"
           :class="{ 'dataset-list-row--hovered': _isHovered, 'dataset-list-row--selected': isSelected }"
           @mouseenter="_isHovered = true"
           @mouseleave="_isHovered = false">
        <!-- Selection checkbox - fixed position on left, visible on hover or when selected -->
        <QItemSection side class="selection-control" :class="{ 'selection-control--visible': _isHovered || isSelected }">
            <QCheckbox v-model="isSelected" dense />
        </QItemSection>

        <QItemSection>
            <!-- Badges row -->
            <div class="row items-center q-gutter-xs q-mb-xs">
                <QBadge v-if="dataset.sharing_status === 'own'" color="blue-2" text-color="blue-9">
                    Created by you
                </QBadge>
                <QBadge v-if="dataset.sharing_status === 'shared' && _creator == null"
                        color="blue-2" text-color="blue-9">
                    Shared with you
                </QBadge>
                <QBadge v-if="dataset.sharing_status === 'shared' && _creator != null"
                        color="blue-2" text-color="blue-9">
                    Shared by {{ _creator }}
                </QBadge>
                <QBadge v-for="tag of dataset.tags" :key="tag" color="green-2" text-color="green-9">
                    {{ tag }}
                </QBadge>
                <QBadge v-if="_publication != null"
                        color="purple-2" text-color="purple-9"
                        class="cursor-pointer"
                        @click="window.location.href = `https://doi.org/${_publication.doi_name}`">
                    <QIcon name="link" size="xs" class="q-mr-xs" />
                    {{ _publication.doi_name }}
                </QBadge>
                <img v-if="_publication != null"
                     height="16"
                     :src="`/static/images/cc/${_publication.license}.svg`"
                     title="Creative Commons license">
            </div>

            <!-- Title -->
            <div class="row items-center q-mb-xs">
                <QIcon name="layers" color="grey-7" class="q-mr-sm" />
                <a :href="`/ui/dataset-detail/${dataset.id}/`" class="text-subtitle1 text-weight-medium dataset-title-link">
                    {{ dataset.name }}
                </a>
            </div>

            <!-- Thumbnails -->
            <ThumbnailRow class="q-mb-sm" :data-source-list-url="dataset.topographies" />

            <!-- Meta info -->
            <div class="text-caption text-grey-7">
                <span v-if="_publication != null">
                    Published by {{ publicationAuthorsPretty }} on {{ publicationDatePretty }}
                </span>
                <span v-else>
                    <span v-if="_creator != null">Created by {{ _creator }}</span>
                    <span v-if="dataset.creation_datetime != null"> on {{ creationDatePretty }}</span>
                </span>
                <span v-if="dataset.topography_count != null">
                     · {{ dataset.topography_count }} measurement<span v-if="dataset.topography_count !== 1">s</span>
                </span>
                <span v-if="dataset.version != null">
                     · v{{ dataset.version }}
                </span>
            </div>

            <!-- Description (truncated) -->
            <div v-if="dataset.description != null && dataset.description !== ''"
                 class="text-body2 text-grey-8 dataset-description q-mt-xs">
                {{ dataset.description }}
            </div>
        </QItemSection>

        <!-- Action buttons - visible on hover -->
        <QItemSection side top class="action-buttons" :class="{ 'action-buttons--visible': _isHovered }">
            <div class="column q-gutter-xs">
                <QBtn flat dense round icon="visibility"
                      :href="`/ui/dataset-detail/${ dataset.id }/`"
                      title="View" />
                <QBtn flat dense round icon="analytics"
                      :href="`/ui/analysis-list/?subjects=${subjectsToBase64({surface: [dataset.id]})}`"
                      title="Analyze" />
                <QBtn flat dense round icon="download"
                      :href="dataset.api.download"
                      title="Download" />
            </div>
        </QItemSection>
    </QItem>
</template>

<style scoped>
/* MD3 list item states */
.dataset-list-row {
    transition: background-color 0.2s ease;
    padding: 12px 16px;
}

.dataset-list-row--hovered {
    background-color: rgba(0, 0, 0, 0.04);
}

.dataset-list-row--selected {
    background-color: rgba(var(--q-primary-rgb, 25, 118, 210), 0.08);
}

.dataset-list-row--selected.dataset-list-row--hovered {
    background-color: rgba(var(--q-primary-rgb, 25, 118, 210), 0.12);
}

/* Selection checkbox - fixed width on left, fades in on hover or when selected */
.selection-control {
    width: 40px;
    min-width: 40px;
    opacity: 0;
    transition: opacity 0.2s ease;
}

.selection-control--visible {
    opacity: 1;
}

/* Action buttons - hidden by default, shown on hover */
.action-buttons {
    opacity: 0;
    transition: opacity 0.2s ease;
}

.action-buttons--visible {
    opacity: 1;
}

/* Title link styling */
.dataset-title-link {
    color: inherit;
    text-decoration: none;
    transition: color 0.15s ease;
}

.dataset-title-link:hover {
    color: var(--q-primary);
}

/* The following cuts the description text after 2 display lines */
.dataset-description {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
</style>