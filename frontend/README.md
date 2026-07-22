# Frontend

Vue 3 single-page components for the *contact.engineering* UI. The code is
bundled by webpack (see `webpack.config.js` in the repository root) into
`static/js/app.bundle.js`, which exposes `topobank.app.createAppFrame`. The
Django app (`ce_ui`) mounts a page component by passing its registered name
as `vue_component` (see `ce_ui/templates/app.html`).

## Directory structure

```
frontend/
├── app.ts              Entry point; creates the Vue app and registers components
├── pages/              Page-level components, one per Django view,
│                       registered by name in pages/index.ts
├── components/
│   ├── analysis/       Analysis cards and task-state UI; the cards are
│   │                   registered globally in components/analysis/index.ts
│   │                   (they are instantiated by name from server data)
│   ├── layout/         App chrome: AppFrame, top navigation, breadcrumbs,
│   │                   offcanvases, version information
│   ├── manager/        Dataset (digital surface twin) and measurement
│   │                   management
│   ├── publish/        Publication wizard
│   └── ui/             Generic, domain-independent widgets (plots, drop
│   │                   zone, spinners, modals)
├── stores/             Pinia stores
├── utils/              Framework-free TypeScript modules with unit tests
└── scss/               Stylesheets
```

## Conventions

- **File naming**: Vue single-file components are `PascalCase.vue`;
  TypeScript modules are `camelCase.ts`. Component registries are `index.ts`.
- **Imports**: always use the `@/` alias (which maps to `frontend/`), never
  relative paths or the package name. The alias is configured in
  `webpack.config.js`, `tsconfig.json` and `vitest.config.ts`.
- **Logic vs. presentation**: functional (pure) logic lives in `utils/` as
  plain TypeScript so it can be unit-tested without a DOM or Vue. Components
  should only contain state wiring, API calls and templates.
- **Tests**: each `utils/` module has a sibling `<name>.test.ts` file, run
  with [vitest](https://vitest.dev):

  ```sh
  npm test         # run once
  npm run test-watch
  ```

- **Building**:

  ```sh
  npm run build-dev   # development build to static/js/
  npm run build-prod  # production build
  npm run dev         # watch mode, output one directory up (../static/js)
  ```
