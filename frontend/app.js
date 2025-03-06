// Vue & Bokeh
import {createApp} from 'vue';
import {createBootstrap} from 'bootstrap-vue-next'

// Axios
import axios from "axios";

// Import the app components
import {componentIndex} from './index.js';

// Import the AppFrame component
import AppFrame from './base/AppFrame.vue';

/**
 * Create Vue.js app for a component and hook it up to DOM element
 */
export function createAppFrame(element, csrfToken, appProps, componentProps) {
    let app = createApp(AppFrame, componentProps);
    app.use(createBootstrap());
    axios.defaults.headers.common['X-CSRFToken'] = csrfToken;
    app.provide('csrfToken', csrfToken);
    app.provide('appProps', appProps);
    // Register all single-page components from the index
    for (const component of componentIndex) {
        app.component(component.name, component.implementation);
    }
    app.mount(element);
    return app;
}
