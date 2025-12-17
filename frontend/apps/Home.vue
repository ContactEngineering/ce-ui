<script setup lang="ts">

import { inject, onMounted, ref } from "vue";
import { QCard, QCardSection, QBtn, QIcon, QImg } from "quasar";
import { managerApiStatisticsRetrieve, analysisApiStatisticsRetrieve } from "@/api";

const appProps = inject("appProps");

const managerStatistics = ref(null);
const analysisStatistics = ref(null);

onMounted(async () => {
    try {
        const managerResponse = await managerApiStatisticsRetrieve();
        managerStatistics.value = managerResponse.data;
    } catch (error) {
        console.warn("Failed to load manager statistics:", error);
    }
    try {
        const analysisResponse = await analysisApiStatisticsRetrieve();
        analysisStatistics.value = analysisResponse.data;
    } catch (error) {
        console.warn("Failed to load analysis statistics:", error);
    }
});

</script>

<template>
    <div class="q-pa-md">
        <!-- Hero Section -->
        <div class="text-center q-mb-xl">
            <div class="text-h3 q-mb-md">
                Welcome to <span class="text-weight-bold">contact.&#8203;engineering</span>
            </div>
            <div class="text-subtitle1 text-grey-7 q-mx-auto" style="max-width: 800px;">
                A web-based application for storing and organizing surface measurements,
                characterizing surface topography, analyzing contact properties, and
                sharing or publishing your datasets.
                <a href="https://doi.org/10.1088/2051-672X/ac860a" target="_blank" class="text-primary">
                    Read the accompanying open access paper.
                </a>
            </div>
        </div>

        <!-- Anonymous User: Feature Showcase -->
        <div v-if="appProps.userIsAnonymous" class="row q-col-gutter-lg q-mb-xl">
            <div class="col-12 col-md-6">
                <QCard>
                    <QImg src="/static/images/screenshot_psd.jpg" :ratio="16/9" />
                    <QCardSection>
                        <div class="text-subtitle1 text-weight-medium">Statistical Analysis</div>
                        <div class="text-body2 text-grey-7">
                            Combine analyses on multiple measurements into a complete
                            statistical representation of a surface.
                        </div>
                    </QCardSection>
                    <QCardSection class="q-pt-none">
                        <QBtn
                            flat
                            color="primary"
                            label="See example"
                            href="/ui/analysis-detail/topobank_statistics.power_spectral_density/?subjects=eyJzdXJmYWNlIjpbMTg4OV19"
                        />
                    </QCardSection>
                </QCard>
            </div>
            <div class="col-12 col-md-6">
                <QCard>
                    <QImg src="/static/images/screenshot_contact_mechanics.jpg" :ratio="16/9" />
                    <QCardSection>
                        <div class="text-subtitle1 text-weight-medium">Contact Mechanics</div>
                        <div class="text-body2 text-grey-7">
                            Carry out contact mechanical calculations with the
                            boundary element method.
                        </div>
                    </QCardSection>
                    <QCardSection class="q-pt-none">
                        <QBtn
                            flat
                            color="primary"
                            label="See example"
                            href="/ui/analysis-detail/topobank_contact.boundary_element_method/?subjects=eyJ0b3BvZ3JhcGh5IjpbMTk1OF19"
                        />
                    </QCardSection>
                </QCard>
            </div>
        </div>

        <!-- Authenticated User: Statistics Cards -->
        <div v-else class="row q-col-gutter-md q-mb-xl">
            <div class="col-12 col-sm-6 col-lg-3">
                <a :href="appProps.datasetListUrl" class="text-decoration-none">
                    <QCard flat bordered class="full-height">
                        <QCardSection class="row items-center no-wrap">
                            <QIcon name="layers" size="48px" color="primary" class="q-mr-md" />
                            <div>
                                <div class="text-h4 text-primary">{{ managerStatistics?.nb_surfaces_of_user ?? '-' }}</div>
                                <div class="text-body2 text-grey-7">Digital surface twins</div>
                            </div>
                        </QCardSection>
                    </QCard>
                </a>
            </div>
            <div class="col-12 col-sm-6 col-lg-3">
                <a :href="appProps.datasetListUrl" class="text-decoration-none">
                    <QCard flat bordered class="full-height">
                        <QCardSection class="row items-center no-wrap">
                            <QIcon name="science" size="48px" color="red" class="q-mr-md" />
                            <div>
                                <div class="text-h4 text-red">{{ managerStatistics?.nb_topographies_of_user ?? '-' }}</div>
                                <div class="text-body2 text-grey-7">Individual measurements</div>
                            </div>
                        </QCardSection>
                    </QCard>
                </a>
            </div>
            <div class="col-12 col-sm-6 col-lg-3">
                <a :href="appProps.datasetListUrl" class="text-decoration-none">
                    <QCard flat bordered class="full-height">
                        <QCardSection class="row items-center no-wrap">
                            <QIcon name="area_chart" size="48px" color="orange" class="q-mr-md" />
                            <div>
                                <div class="text-h4 text-orange">{{ analysisStatistics?.nb_analyses_of_user ?? '-' }}</div>
                                <div class="text-body2 text-grey-7">Computed analyses</div>
                            </div>
                        </QCardSection>
                    </QCard>
                </a>
            </div>
            <div class="col-12 col-sm-6 col-lg-3">
                <a :href="appProps.datasetListUrl" class="text-decoration-none">
                    <QCard flat bordered class="full-height">
                        <QCardSection class="row items-center no-wrap">
                            <QIcon name="share" size="48px" color="green" class="q-mr-md" />
                            <div>
                                <div class="text-h4 text-green">{{ managerStatistics?.nb_surfaces_shared_with_user ?? '-' }}</div>
                                <div class="text-body2 text-grey-7">Shared with you</div>
                            </div>
                        </QCardSection>
                    </QCard>
                </a>
            </div>
        </div>

        <!-- Authenticated User: Feature Explanation -->
        <div v-if="!appProps.userIsAnonymous" class="row q-col-gutter-md">
            <div class="col-12 col-md-6 col-lg-3">
                <QCard flat bordered class="full-height">
                    <QCardSection>
                        <div class="row items-center q-mb-sm">
                            <QIcon name="layers" color="primary" size="24px" class="q-mr-sm" />
                            <div class="text-h6">Digital Surface Twins</div>
                        </div>
                        <div class="text-body2 text-grey-7">
                            A digital surface twin represents the real-life surface you are measuring,
                            together with its descriptive metadata. If you make multiple measurements on
                            the same real-world surface (even using different techniques), you can collect
                            all the measurements together in a single digital surface twin.
                        </div>
                    </QCardSection>
                </QCard>
            </div>
            <div class="col-12 col-md-6 col-lg-3">
                <QCard flat bordered class="full-height">
                    <QCardSection>
                        <div class="row items-center q-mb-sm">
                            <QIcon name="science" color="red" size="24px" class="q-mr-sm" />
                            <div class="text-h6">Measurements</div>
                        </div>
                        <div class="text-body2 text-grey-7">
                            For each digital surface twin, you must upload one or more measurements.
                            These represent each individual measurement you performed. You can save
                            metadata for each one, and perform basic pre-analysis.
                        </div>
                    </QCardSection>
                </QCard>
            </div>
            <div class="col-12 col-md-6 col-lg-3">
                <QCard flat bordered class="full-height">
                    <QCardSection>
                        <div class="row items-center q-mb-sm">
                            <QIcon name="area_chart" color="orange" size="24px" class="q-mr-sm" />
                            <div class="text-h6">Analysis Workflows</div>
                        </div>
                        <div class="text-body2 text-grey-7">
                            A number of analysis workflows, such as computing the power-spectral density
                            or the real area of contact, are performed on-demand on all uploaded measurements.
                            Multiple analyses can be averaged to create the joint power-spectral density
                            of a digital surface twin.
                        </div>
                    </QCardSection>
                </QCard>
            </div>
            <div class="col-12 col-md-6 col-lg-3">
                <QCard flat bordered class="full-height">
                    <QCardSection>
                        <div class="row items-center q-mb-sm">
                            <QIcon name="share" color="green" size="24px" class="q-mr-sm" />
                            <div class="text-h6">Sharing & Publishing</div>
                        </div>
                        <div class="text-body2 text-grey-7">
                            Digital surface twins can be shared with others for collaboration. You
                            decide whether your collaborators can modify them or not. They can also
                            be published to make them citable and accessible for everyone.
                        </div>
                    </QCardSection>
                </QCard>
            </div>
        </div>

        <!-- Anonymous User: Call to Action -->
        <div v-else class="row q-col-gutter-lg">
            <div class="col-12 col-md-6">
                <QCard flat bordered class="full-height">
                    <QCardSection>
                        <div class="row items-center q-mb-md">
                            <QIcon name="public" color="primary" size="32px" class="q-mr-sm" />
                            <div class="text-h5">Browse Published Data</div>
                        </div>
                        <div class="text-body1 text-grey-7 q-mb-md">
                            A digital surface twin combines multiple measurements of a real-life surface,
                            together with descriptive metadata. Explore our public library of published datasets.
                        </div>
                    </QCardSection>
                    <QCardSection class="q-pt-none">
                        <QBtn
                            unelevated
                            color="primary"
                            icon="search"
                            label="Browse public library"
                            :href="appProps.datasetListUrl"
                        />
                    </QCardSection>
                </QCard>
            </div>
            <div class="col-12 col-md-6">
                <QCard flat bordered class="full-height">
                    <QCardSection>
                        <div class="row items-center q-mb-md">
                            <QIcon name="login" color="primary" size="32px" class="q-mr-sm" />
                            <div class="text-h5">Sign In to Upload</div>
                        </div>
                        <div class="text-body1 text-grey-7 q-mb-md">
                            Sign in with your ORCID account to upload measurements and create your own
                            digital surface twins. If you don't have an ORCID account yet, you can register.
                        </div>
                    </QCardSection>
                    <QCardSection class="q-pt-none">
                        <QBtn
                            unelevated
                            color="primary"
                            icon="login"
                            label="Sign in with ORCID"
                            :href="appProps.loginUrl"
                        />
                    </QCardSection>
                </QCard>
            </div>
        </div>
    </div>
</template>

<style scoped>
.full-height {
    height: 100%;
}
.text-decoration-none {
    text-decoration: none;
}
</style>
