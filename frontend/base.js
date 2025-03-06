// Vue & Bokeh
import {createApp} from 'vue';
import {createBootstrap} from 'bootstrap-vue-next'

// Axios
import axios from "axios";

// Import the app components
import './index.js';

// Import the AppFrame component
import AppFrame from './base/AppFrame.vue';

/**
 * Create Vue.js app for a component and hook it up to DOM element
 */
export function createAppFrame(element, csrfToken, props) {
    let app = createApp(AppFrame, props);
    app.use(createBootstrap());
    axios.defaults.headers.common['X-CSRFToken'] = csrfToken;
    app.provide('csrfToken', csrfToken);
    app.mount(element);
    return app;
}
