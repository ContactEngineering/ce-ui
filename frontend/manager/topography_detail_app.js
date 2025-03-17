import axios from "axios";
import {createApp} from 'vue';
import {createBootstrap} from "bootstrap-vue-next";

import TopographyDetail from './TopographyDetail.vue';


export function createTopographyDetailApp(el, csrfToken, props) {
    let app = createApp(TopographyDetail, props);
    app.use(createBootstrap());
    axios.defaults.headers.common['X-CSRFToken'] = csrfToken;
    app.provide('csrfToken', csrfToken);
    app.mount(el);
    return app;
}
