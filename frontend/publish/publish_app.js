import { createApp } from 'vue';
import { createBootstrap } from 'bootstrap-vue-next';
import VueCookies from 'vue-cookies';

import Publish from './Publish.vue';

import axios from "axios";
import mitt from 'mitt';

const eventHub = mitt();

export function createPublishApp(el, csrfToken, props) {
	let app = createApp(Publish, props);
	app.use(createBootstrap());
	app.use(VueCookies);
	axios.defaults.headers.common['X-CSRFToken'] = csrfToken;
	app.provide('csrfToken', csrfToken);
	app.provide('eventHub', eventHub);
	app.mount(el);
	return app;
}
