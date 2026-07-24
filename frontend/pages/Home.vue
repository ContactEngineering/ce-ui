<script setup lang="ts">

import axios from "axios";
import {computed, inject, onMounted, ref} from "vue";

const props = defineProps({
    managerStatisticsApiUrl: {
        type: String,
        default: "/manager/api/statistics"
    },
    analysisStatisticsApiUrl: {
        type: String,
        default: "/analysis/api/statistics"
    }
});

const appProps = inject("appProps");

const managerStatistics = ref(null);
const analysisStatistics = ref(null);

onMounted(() => {
    axios.get(props.managerStatisticsApiUrl).then(response => {
        managerStatistics.value = response.data;
    });
    axios.get(props.analysisStatisticsApiUrl).then(response => {
        analysisStatistics.value = response.data;
    });
});

// Stat tiles for signed-in users. `accent` drives the tile's top rule and icon
// color via a CSS custom property, so the palette stays theme-driven.
const stats = computed(() => [
    {
        icon: "fa fa-layer-group",
        label: "Digital surface twins",
        value: managerStatistics.value?.nb_surfaces_of_user,
        accent: "var(--bs-primary)"
    },
    {
        icon: "fa fa-microscope",
        label: "Measurements",
        value: managerStatistics.value?.nb_topographies_of_user,
        accent: "var(--bs-info)"
    },
    {
        icon: "fa fa-chart-area",
        label: "Computed analyses",
        value: analysisStatistics.value?.nb_analyses_of_user,
        accent: "var(--bs-success)"
    },
    {
        icon: "fa fa-fw fa-share-alt",
        label: "Shared with you",
        value: managerStatistics.value?.nb_surfaces_shared_with_user,
        accent: "var(--bs-dark)"
    }
]);

</script>

<template>
    <div class="home container py-2">
        <!-- Hero: the one bold band -->
        <section class="home-hero rounded-3 overflow-hidden mb-4">
            <div class="row g-0 align-items-stretch">
                <div class="col-lg-6 p-4 p-lg-5 d-flex flex-column justify-content-center">
                    <p class="home-eyebrow">The openI repository for topography data</p>
                    <h1 class="home-title">contact.<wbr>engineering</h1>
                    <p class="home-lead">
                        Store and organize surface measurements, characterize
                        topography, and compute contact properties — then share or
                        publish your datasets.
                    </p>
                    <div class="d-flex flex-wrap gap-2 mt-4">
                        <a :href="appProps.datasetListUrl" class="btn btn-primary btn-lg">
                            <i class="fa fa-layer-group me-2"></i>
                            {{ appProps.userIsAnonymous ? "Browse the public library" : "Go to your datasets" }}
                        </a>
                        <a v-if="appProps.userIsAnonymous" id="orcid-log-in-link"
                           :href="appProps.loginUrl" class="btn btn-outline-light btn-lg">
                            Sign in with ORCID
                        </a>
                    </div>
                    <p class="home-note mt-3 mb-0">
                        Read the
                        <a target="_blank"
                           href="https://doi.org/10.1088/2051-672X/ac860a">open-access
                            paper</a> for more on the platform.
                    </p>
                </div>
                <div class="col-lg-6 home-media">
                    <img src="/static/images/screenshot_psd.jpg"
                         alt="Power-spectral density analysis of a measured surface"/>
                </div>
            </div>
        </section>

        <!-- Signed in: your data at a glance -->
        <div v-if="!appProps.userIsAnonymous" class="row g-3 mb-4">
            <div v-for="stat in stats" :key="stat.label" class="col-xl-3 col-sm-6">
                <a :href="appProps.datasetListUrl" class="text-decoration-none">
                    <div class="stat-tile h-100" :style="{ '--accent': stat.accent }">
                        <div class="stat-head">
                            <i :class="stat.icon" class="stat-icon"></i>
                            <span class="stat-label">{{ stat.label }}</span>
                        </div>
                        <div class="stat-value">{{ stat.value ?? "—" }}</div>
                    </div>
                </a>
            </div>
        </div>

        <!-- Anonymous: example showcase -->
        <div v-else class="row g-3 mb-4">
            <div class="col-md-6">
                <div class="example-card h-100">
                    <a href="/ui/analysis-detail/topobank_statistics.power_spectral_density/?subjects=eyJzdXJmYWNlIjpbMTg4OV19">
                        <img class="example-img" src="/static/images/screenshot_psd.jpg"
                             alt="Power-spectral density example"/>
                    </a>
                    <div class="example-body">
                        <h2 class="h5">Statistical surface characterization</h2>
                        <p class="text-secondary mb-3">
                            Combine analyses across many measurements into a complete
                            statistical representation of a surface.
                        </p>
                        <a class="btn btn-outline-primary btn-sm"
                           href="/ui/analysis-detail/topobank_statistics.power_spectral_density/?subjects=eyJzdXJmYWNlIjpbMTg4OV19">
                            See an example
                        </a>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="example-card h-100">
                    <a href="/ui/analysis-detail/topobank_contact.boundary_element_method/?subjects=eyJ0b3BvZ3JhcGh5IjpbMTk1OF19">
                        <img class="example-img"
                             src="/static/images/screenshot_contact_mechanics.jpg"
                             alt="Contact mechanics example"/>
                    </a>
                    <div class="example-body">
                        <h2 class="h5">Contact mechanics</h2>
                        <p class="text-secondary mb-3">
                            Run boundary-element contact calculations directly on your
                            measured topographies.
                        </p>
                        <a class="btn btn-outline-primary btn-sm"
                           href="/ui/analysis-detail/topobank_contact.boundary_element_method/?subjects=eyJ0b3BvZ3JhcGh5IjpbMTk1OF19">
                            See an example
                        </a>
                    </div>
                </div>
            </div>
        </div>

        <!-- What the platform does (everyone) -->
        <div class="row g-4 feature-row">
            <div class="col-md-3">
                <i class="fa fa-layer-group feature-icon"></i>
                <h3 class="h6 mt-2">Digital surface twins</h3>
                <p class="text-secondary">A <em>digital surface twin</em> represents a
                    real-life surface together with its metadata. Collect multiple
                    <em>measurements</em> of the same surface — even from different
                    techniques — into one twin.</p>
            </div>
            <div class="col-md-3">
                <i class="fa fa-microscope feature-icon"></i>
                <h3 class="h6 mt-2">Measurements</h3>
                <p class="text-secondary">Upload one or more <em>measurements</em> per
                    twin. Save metadata for each, and run basic pre-analysis on
                    upload.</p>
            </div>
            <div class="col-md-3">
                <i class="fa fa-chart-area feature-icon"></i>
                <h3 class="h6 mt-2">Analysis workflows</h3>
                <p class="text-secondary"><em>Analysis workflows</em> — such as
                    power-spectral density or real contact area — run on demand across
                    your measurements, and can be averaged over a whole twin.</p>
            </div>
            <div class="col-md-3">
                <i class="fa fa-share-alt feature-icon"></i>
                <h3 class="h6 mt-2">Sharing &amp; publishing</h3>
                <p class="text-secondary"><em>Share</em> twins with collaborators
                    (read-only or editable), or <em>publish</em> them to make them
                    citable and openly accessible.</p>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* Hero — the single dark band, everything else stays light and quiet */
.home-hero {
    background-color: var(--bs-dark);
    color: var(--bs-light);
}

.home-eyebrow {
    text-transform: uppercase;
    letter-spacing: .12em;
    font-size: .8rem;
    font-weight: 600;
    color: var(--bs-warning);
    margin-bottom: .5rem;
}

.home-title {
    font-weight: 700;
    font-size: clamp(2rem, 4vw, 3rem);
    line-height: 1.1;
    margin-bottom: 1rem;
}

.home-lead {
    color: rgba(255, 255, 255, .82);
    font-size: 1.1rem;
    max-width: 46ch;
    margin-bottom: 0;
}

.home-note {
    font-size: .85rem;
    color: rgba(255, 255, 255, .6);
}

.home-note a {
    color: var(--bs-warning);
}

.home-media {
    min-height: 260px;
}

.home-media img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}

/* Stat tiles — clean surfaces, palette used only as a thin accent */
.stat-tile {
    background-color: var(--bs-white);
    border: 1px solid var(--bs-border-color);
    border-top: 3px solid var(--accent, var(--bs-primary));
    border-radius: var(--bs-border-radius-lg);
    padding: 1.25rem 1.25rem 1.35rem;
    transition: box-shadow .15s ease, transform .15s ease;
}

a:hover > .stat-tile {
    box-shadow: 0 .5rem 1.25rem rgba(37, 49, 34, .12);
    transform: translateY(-2px);
}

.stat-head {
    display: flex;
    align-items: center;
    gap: .5rem;
    color: var(--bs-secondary-color);
}

.stat-icon {
    color: var(--accent);
}

.stat-label {
    font-size: .78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .06em;
}

.stat-value {
    font-family: var(--bs-font-monospace);
    font-size: 2.5rem;
    font-weight: 600;
    line-height: 1.1;
    color: var(--bs-emphasis-color);
    margin-top: .4rem;
}

/* Example cards (anonymous) — CTA always visible, subtle lift on hover */
.example-card {
    background-color: var(--bs-white);
    border: 1px solid var(--bs-border-color);
    border-radius: var(--bs-border-radius-lg);
    overflow: hidden;
    transition: box-shadow .15s ease, transform .15s ease;
}

.example-card:hover {
    box-shadow: 0 .5rem 1.25rem rgba(37, 49, 34, .12);
    transform: translateY(-2px);
}

.example-img {
    width: 100%;
    aspect-ratio: 16 / 9;
    object-fit: cover;
    display: block;
    border-bottom: 1px solid var(--bs-border-color);
}

.example-body {
    padding: 1.25rem;
}

/* Feature row */
.feature-icon {
    font-size: 1.4rem;
    color: var(--bs-primary);
}

.feature-row h3 {
    font-weight: 600;
}
</style>
