<script setup lang="ts">

import {inject, onMounted, ref} from "vue";
import {managerApiStatisticsRetrieve, analysisApiStatisticsRetrieve} from "@/api";

const appProps = inject("appProps");

const managerStatistics = ref(null);
const analysisStatistics = ref(null);

onMounted(async () => {
    const managerResponse = await managerApiStatisticsRetrieve();
    managerStatistics.value = managerResponse.data;
    const analysisResponse = await analysisApiStatisticsRetrieve();
    analysisStatistics.value = analysisResponse.data;
});

</script>

<template>
    <div class="tab-content mt-1">
        <div class="tab-pane active">
            <div class="jumbotron">
                <div class="container">
                    <h1 class="display-5">Welcome to <b>contact.&#8203;engineering</b>
                    </h1>
                    <p class="lead">This is a web-based application that allows you to:
                        Store and organize surface measurements,
                        characterize surface topography,
                        analyze contact properties and
                        (if you wish) share your data with collaborators or even publish
                        your datasets.
                        For more information on this site
                        <a class="alert-link" target="_blank"
                           href="https://doi.org/10.1088/2051-672X/ac860a">
                            please read the accompanying open access paper</a>.
                    </p>
                </div>
            </div>
            <div class="container">
                <div v-if="appProps.userIsAnonymous"
                     class="row">
                    <div class="col-6">
                        <div class="opacity-container">
                            <a href="/ui/analysis-detail/topobank_statistics.power_spectral_density/?subjects=eyJzdXJmYWNlIjpbMTg4OV19">
                                <img class="image"
                                     src="/static/images/screenshot_psd.jpg"
                                     width="100%"/>
                            </a>
                            <div class="middle">
                                <a href="/ui/analysis-detail/topobank_statistics.power_spectral_density/?subjects=eyJzdXJmYWNlIjpbMTg4OV19"
                                   class="btn btn-secondary">
                                    Combine analyses on multiple measurements into a
                                    complete
                                    statistical representation of a surface.
                                    <em>Click to see an example.</em>
                                </a>
                            </div>
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="opacity-container">
                            <a href="/ui/analysis-detail/topobank_contact.boundary_element_method/?subjects=eyJ0b3BvZ3JhcGh5IjpbMTk1OF19">
                                <img class="image"
                                     src="/static/images/screenshot_contact_mechanics.jpg"
                                     width="100%"/>
                            </a>
                            <div class="middle">
                                <a href="/ui/analysis-detail/topobank_contact.boundary_element_method/?subjects=eyJ0b3BvZ3JhcGh5IjpbMTk1OF19"
                                   class="btn btn-secondary">
                                    Carry out contact mechanical calculations with the
                                    boundary element method.
                                    <em>Click to see an example.</em>
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
                <div v-else class="row">
                    <div class="col-xl-3 col-sm-6 mb-3">
                        <a :href="appProps.datasetListUrl"
                           class="card-link text-decoration-none">
                            <div class="card text-white bg-primary o-hidden h-100">
                                <div class="card-body">
                                    <div class="card-body-icon">
                                        <i class="fa fa-layer-group"></i>
                                    </div>
                                    <div class="me-2">
                                        You have
                                        <div class="welcome-page-statistics">
                                            {{ managerStatistics?.nb_surfaces_of_user }}
                                        </div>
                                        digital surface twins.
                                    </div>
                                </div>
                            </div>
                        </a>
                    </div>
                    <div class="col-xl-3 col-sm-6 mb-3">
                        <a :href="appProps.datasetListUrl"
                           class="card-link text-decoration-none">
                            <div class="card text-white bg-danger o-hidden h-100">
                                <div class="card-body">
                                    <div class="card-body-icon">
                                        <i class="fa fa-microscope"></i>
                                    </div>
                                    <div class="me-2">
                                        You have
                                        <div class="welcome-page-statistics">
                                            {{ managerStatistics?.nb_topographies_of_user }}
                                        </div>
                                        individual measurements.
                                    </div>
                                </div>
                            </div>
                        </a>
                    </div>
                    <div class="col-xl-3 col-sm-6 mb-3">
                        <a :href="appProps.datasetListUrl"
                           class="card-link text-decoration-none">
                            <div class="card text-white bg-warning o-hidden h-100">
                                <div class="card-body">
                                    <div class="card-body-icon">
                                        <i class="fa fa-chart-area"></i>
                                    </div>
                                    <div class="me-2">
                                        You have
                                        <div class="welcome-page-statistics">
                                            {{ analysisStatistics?.nb_analyses_of_user }}
                                        </div>
                                        computed analyses.
                                    </div>
                                </div>
                            </div>
                        </a>
                    </div>
                    <div class="col-xl-3 col-sm-6 mb-3">
                        <a :href="appProps.datasetListUrl"
                           class="card-link text-decoration-none">
                            <div class="card text-white bg-success o-hidden h-100">
                                <div class="card-body">
                                    <div class="card-body-icon">
                                        <i class="fa fa-fw fa-share-alt"></i>
                                    </div>
                                    <div class="me-2">
                                        You have access to
                                        <div class="welcome-page-statistics">
                                            {{
                                                managerStatistics?.nb_surfaces_shared_with_user
                                            }}
                                        </div>
                                        digital twins of other users.
                                    </div>
                                </div>
                            </div>
                        </a>
                    </div>
                </div>
            </div>
            <div class="container">
                <div v-if="!appProps.userIsAnonymous" class="row">
                    <div class="col-md-3">
                        <h4>Digital surface twins</h4>
                        <p>A <em>digital surface twin</em> represents the real-life
                            surface you are measuring,
                            together with its
                            descriptive metadata. If you make multiple measurements on
                            the same real-world surface
                            (even using
                            different techniques), you can collect all the <em>measurements</em>
                            together in a
                            single <em>digital
                                surface twin</em>.
                        </p>
                    </div>
                    <div class="col-md-3">
                        <h4>Measurements</h4>
                        <p>For each <em>digital surface twin</em>, you must upload one
                            or more <em>measurements</em>.
                            These represent each
                            individual measurement you performed. You can save metadata
                            for each one, and perform
                            basic pre-analysis.
                        </p>
                    </div>
                    <div class="col-md-3">
                        <h4>Analysis workflows</h4>
                        <p>A number of <em>analysis workflows</em>, such as computing
                            the power-spectral density or
                            the real area
                            of contact, are performed on-demand on all uploaded <em>measurements</em>.
                            Multiple analyses can be averaged to create, for example,
                            the joint power-spectral
                            density of a <em>digital surface twin</em>.
                        </p>
                    </div>
                    <div class="col-md-3">
                        <h4>Sharing & publishing</h4>
                        <p><em>Digital surface twins</em> can be <em>shared</em> with
                            others for collaboration. You
                            decide whether
                            your collaborators can modify them or not.</p>
                        <p>Digital surface twins can also be <em>published</em> to make
                            them citable and accessible
                            for everyone.</p>
                    </div>
                </div>
                <div v-else class="row">
                    <div class="col-md-6">
                        <h2>Browse published digital surface twins</h2>
                        <p>A <em>digital surface twin</em> combines multiple
                            measurements of a real-life surface,
                            together with descriptive metadata.
                            <a id="orcid-log-in-link" class="btn btn-secondary"
                               :href="appProps.datasetListUrl">
                                Browse public library of digital surface twins
                            </a>
                        </p>
                    </div>
                    <div class="col-md-6">
                        <h2>Sign in to upload measurements</h2>
                        <p>
                            Please allow the ORCID site to authenticate yourself to
                            contact.engineering.
                            If you don't have an ORCID account yet, you will be able to
                            register.
                        </p>
                        <a id="orcid-log-in-link" class="btn btn-secondary"
                           :href="appProps.loginUrl">
                            Sign in using your ORCID account
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>