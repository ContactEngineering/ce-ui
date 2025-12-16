// Vue, Pinia and Quasar
import {createApp} from 'vue';
import {Quasar, Notify, Dialog, Loading} from 'quasar';
import {createPinia} from "pinia";
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';

// Quasar styles
import '@quasar/extras/material-icons/material-icons.css';
import 'quasar/dist/quasar.css';

// Axios
import axios from "axios";

// Generated API client
import {client} from "@/api/client.gen";

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
    app.use(Quasar, {
        plugins: {Notify, Dialog, Loading},
        config: {
            // MD3-style brand colors
            brand: {
                primary: '#1976D2',
                secondary: '#535F70',
                accent: '#6B5778',
                dark: '#1A1C1E',
                positive: '#386A1F',
                negative: '#BA1A1A',
                info: '#0061A4',
                warning: '#7D5700'
            },
            // MD3-style notifications
            notify: {
                position: 'top',
                timeout: 4000,
                progress: true,
                classes: 'rounded-lg'
            },
            // MD3-style loading indicator
            loading: {
                spinnerColor: 'primary',
                backgroundColor: 'white',
                spinnerSize: 80
            }
        }
    });
    axios.defaults.headers.common['X-CSRFToken'] = csrfToken;
    axios.defaults.withCredentials = true;
    // Configure the generated API client to use the global axios instance
    // This ensures it inherits all defaults (CSRF token, withCredentials, etc.)
    client.setConfig({
        axios: axios,
        baseURL: '',
        headers: {'X-CSRFToken': csrfToken}
    });
    app.provide('csrfToken', csrfToken);
    app.provide('appProps', appProps);
    // Register all single-page components from the index
    registerAppComponents(app);
    // Register all analysis card components from the index
    registerAnalysisCardComponents(app);
    app.mount(element);
    return app;
}
