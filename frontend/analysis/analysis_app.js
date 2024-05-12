import {createApp} from 'vue';
import VueCookies from 'vue-cookies';

import AnalysisResultsList from './AnalysisResultsList.vue';
import AnalysisResultsDetail from './AnalysisResultsDetail.vue';

import ContactMechanicsCard from 'topobank_contact/ContactMechanicsCard.vue';
import RoughnessParametersCard from 'topobank_statistics/RoughnessParametersCard.vue';
import SeriesCard from 'topobank/analysis/SeriesCard.vue';

import axios from "axios";
import mitt from 'mitt';

const eventHub = mitt();

export function registerAnalysisCardComponents(app) {
    app.component('ContactMechanicsCard', ContactMechanicsCard);
    app.component('RoughnessParametersCard', RoughnessParametersCard);
    app.component('SeriesCard', SeriesCard);
}

export function createAnalysisResultsListApp(el, csrfToken, props) {
    let app = createApp(AnalysisResultsList, props);
    app.use(VueCookies);
    axios.defaults.headers.common['X-CSRFToken'] = csrfToken;
    app.provide('csrfToken', csrfToken);
    app.provide('eventHub', eventHub);
    registerAnalysisCardComponents(app);
    app.mount(el);
    return app;
}

export function createAnalysisResultsDetailApp(el, csrfToken, props) {
    let app = createApp(AnalysisResultsDetail, props);
    app.use(VueCookies);
    axios.defaults.headers.common['X-CSRFToken'] = csrfToken;
    app.provide('csrfToken', csrfToken);
    app.provide('eventHub', eventHub);
    registerAnalysisCardComponents(app);
    app.mount(el);
    return app;
}
