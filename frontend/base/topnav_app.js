import axios from "axios";
import {createApp} from 'vue';
import {createBootstrap} from "bootstrap-vue-next";

import UserMenu from './UserMenuButton.vue';

export function createUserMenuApp(el, csrfToken, props) {
    let app = createApp(UserMenu, props);
    app.use(createBootstrap());
    axios.defaults.headers.common['X-CSRFToken'] = csrfToken;
    app.provide('csrfToken', csrfToken);
    app.mount(el);
    return app;
}
