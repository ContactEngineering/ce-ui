// Vue, Pinia and Boostrap
import {createApp} from 'vue';
import {createBootstrap} from 'bootstrap-vue-next'
import {createPinia} from "pinia";
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';


// Axios
import axios from "axios";

// Import the app components
import {registerAppComponents} from './apps/index';
import {registerAnalysisCardComponents} from "./analysis/index";

// Import the AppFrame component
import AppFrame from './apps/AppFrame.vue';

/**
 * Create Vue.js app for a component and hook it up to DOM element
 */
export function createAppFrame(element, csrfToken, appProps, componentProps) {
    let app = createApp(AppFrame, componentProps);
    const pinia = createPinia();
    pinia.use(piniaPluginPersistedstate);
    app.use(pinia);
    app.use(createBootstrap());
    axios.defaults.headers.common['X-CSRFToken'] = csrfToken;
    app.provide('csrfToken', csrfToken);
    app.provide('appProps', appProps);
    // Register all single-page components from the index
    registerAppComponents(app);
    // Register all analysis card components from the index
    registerAnalysisCardComponents(app);
    app.mount(element);
    return app;
}
