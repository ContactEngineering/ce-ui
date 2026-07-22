// Vue, Pinia and Bootstrap
import {createApp} from 'vue';
import {createBootstrap} from 'bootstrap-vue-next';
import {createPinia} from "pinia";
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';

// Axios
import axios from "axios";

// Component registries
import {registerPageComponents} from '@/pages';
import {registerAnalysisCardComponents} from "@/components/analysis";

// The frame component that hosts the page components
import AppFrame from '@/components/layout/AppFrame.vue';

import {getCookie} from "@/utils/cookies";

/**
 * Create Vue.js app for a component and hook it up to DOM element
 */
export function createAppFrame(element, csrfToken: string, appProps, componentProps) {
    let app = createApp(AppFrame, componentProps);
    const pinia = createPinia();
    pinia.use(piniaPluginPersistedstate);
    app.use(pinia);
    app.use(createBootstrap());
    axios.defaults.xsrfCookieName = 'csrftoken';
    axios.defaults.xsrfHeaderName = 'X-CSRFToken';
    axios.defaults.withXSRFToken = true;
    axios.defaults.headers.common['X-CSRFToken'] = csrfToken;
    axios.interceptors.request.use((config) => {
        const token = getCookie('csrftoken') ?? csrfToken;

        if (token !== null && token !== undefined && token !== '') {
            config.headers = config.headers ?? {};
            config.headers['X-CSRFToken'] = token;
        }

        return config;
    });
    app.provide('csrfToken', csrfToken);
    app.provide('appProps', appProps);
    // Register all page and analysis card components from their indices
    registerPageComponents(app);
    registerAnalysisCardComponents(app);
    app.mount(element);
    return app;
}
