// jQuery
import jQuery from 'jquery';

window.$ = window.jQuery = jQuery;

// Vue & Bokeh
import {createApp} from 'vue';
import {createBootstrap} from 'bootstrap-vue-next'
import * as Bokeh from '@bokeh/bokehjs';

window.Bokeh = Bokeh;

import DeepZoomImage from '../components/DeepZoomImage.vue';

import Basket from '../base/Basket.vue'
import DatasetList from './DatasetList.vue';

import 'topobank/scss/custom.scss';
/**
 * Event bus for initiating DZI download
 */
import mitt from 'mitt';
import axios from "axios";

const eventHub = mitt();

/**
 * Return event hub
 */
export function getEventHub() {
    return eventHub;
}

/**
 * Wrapper for an OpenSeadragon instance (with a scale bar)
 */
export function createDeepZoomImage(el, csrfToken, props) {
    let app = createApp(DeepZoomImage, props);
    app.use(createBootstrap());
    axios.defaults.headers.common['X-CSRFToken'] = csrfToken;
    app.provide('csrfToken', csrfToken);
    app.provide('eventHub', eventHub);
    app.mount(el);
    return app;
}

/**
 * Used to display search results/list of digital surface twins
 */
export function createDatasetListApp(el, csrfToken, props) {
    let app = createApp(DatasetList, props);
    app.use(createBootstrap());
    axios.defaults.headers.common['X-CSRFToken'] = csrfToken;
    app.provide('csrfToken', csrfToken);
    app.provide('eventHub', eventHub);
    app.mount(el);
    return app;
}
