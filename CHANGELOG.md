# Changelog for plugin *ce-ui*

## 1.39.0 (not yet released)

- ENH: An account is created with an ORCID iD and no other way. Registration
  with an email address and a password is closed, and a provider outside
  `SOCIALACCOUNT_SIGNUP_PROVIDERS` cannot create an account either; the page
  such an attempt lands on explains how to get one. The ORCID account cannot be
  disconnected afterwards, since it is what identifies the account
- ENH: Google sign-in finds an existing account by email address -- verified by
  Google, and confirmed here -- and connects itself to it, rather than being
  turned away. django-allauth would settle for an address somebody had merely
  claimed without confirming; `SocialAccountAdapter.authenticate_by_email`
  requires a confirmed one, so that a claim cannot capture somebody else's
  sign-in
- ENH: The connected identities page warns when an account has no confirmed
  email address, which leaves it with no Google sign-in, no password sign-in
  and no way to recover
- DOC: `docs/authentication.rst` describes how users sign in and how to obtain
  credentials for each identity provider, including Google's consent screen,
  scope classification and publishing status. It lives here, together with the
  `orcid.yaml.template` and `google.yaml.template` fixtures, because this
  package owns the user model and the provider configuration; topobank is
  agnostic of the sign-in procedure
- MAINT: The `topobank-orcid` distribution was folded into this package as
  `ce_ui.users`, `ce_ui.authorization` and `ce_ui.organizations`. It had a
  single consumer -- this one -- and the seam it filled lives in topobank
  (`AUTH_USER_MODEL`, `TOPOBANK_PERMISSION_MODEL`,
  `TOPOBANK_ORGANIZATION_MODEL`, `TOPOBANK_ANONYMOUS_USER_GETTER`), which is
  unaffected: a deployment with its own user and permission models still
  provides them the same way. The Django app labels (`users`, `authorization`,
  `organizations`) are unchanged, so recorded migrations stay valid and no
  database change is needed. `django-allauth` and `django-notifications-hq`,
  previously pulled in through `topobank-orcid`, are now declared here
- ENH: Sign in with Google, or with an email address and a password, in
  addition to ORCID. The sign-in page offers every provider the deployment has
  configured, and registration with an email address is open by default
  (`ACCOUNT_ALLOW_SIGNUP`, `ACCOUNT_EMAIL_VERIFICATION`)
- ENH: A *Connected identities* page (`/accounts/3rdparty/`) lists the ways a
  user can sign in, connects further providers, and disconnects ones that are
  no longer needed. It is linked from the user menu and the profile page
- ENH: Publishing a dataset or a collection requires a connected ORCID iD. The
  requirement is enforced on the publication endpoints themselves, so it also
  covers API clients, and the publication pages explain it up front instead of
  failing at the end of the form
- MAINT: `appProps.loginUrl` points at the sign-in page rather than at the
  ORCID provider directly, and `appProps.userHasOrcid` and
  `appProps.connectionsUrl` were added

## 1.38.0 (2026-08-04)

- ENH: Analysis cards poll the task states of all their pending analyses in a
  single batched request per tick (v2 `ids` filter) instead of one request per
  analysis every few seconds — running a workflow over a dataset with dozens
  of measurements no longer floods the server with polling traffic
- ENH: The task-status rows share a cache for workflow and subject
  descriptions, so opening the task list of a card makes one request for the
  workflow instead of one per row

## 1.37.0 (2026-08-04)

- ENH: The dataset detail page is server-rendered from the v2 API, which does
  not inline full measurement representations; rendering the page costs a
  handful of database queries instead of ~10 per measurement. The measurement
  cards fetch their data asynchronously, so the page paints immediately
- ENH: The publication details of a published dataset arrive embedded in the
  v2 response instead of requiring a separate request before anything renders
- ENH: The permissions tab runs on the v2 permission-set API
  (grant/revoke endpoints) instead of the v1 whole-list PATCH
- BUG: Tag badges on the dataset detail sidebar rendered empty (they read
  `.name` off what has always been a plain string)

## 1.36.0 (2026-08-04)

- ENH: The dataset list runs on the v2 API and renders each page from a single
  response: creator names, publication details (DOI, license, authors) and
  measurement thumbnails arrive embedded, replacing the two to three requests
  every row used to make on its own
- ENH: Presigned storage URLs are memoized for half their lifetime
  (`ce_ui.storage.CachedPresignedUrlStorage`), so the URL for a thumbnail, a
  plot data series or a deep-zoom tile stays the same between page loads and
  browsers can serve it from their cache instead of re-downloading it
- ENH: Uploaded objects carry a `Cache-Control` header matching that window
- ENH: The "Created by you" / "shared with you" badges on dataset rows work
  again; they relied on a `sharing_status` field that no API version reported

## 1.35.0 (2026-08-04)

- ENH: Analysis cards refresh at most once every ten seconds while a batch of
  tasks is running (plus a final refresh when the batch completes), instead of
  rebuilding the whole card - server round-trip, data-series downloads and all -
  for every single task that finished
- ENH: The dataset list renders thumbnails from the data it already has instead
  of every row fetching its measurements from the API again; thumbnails load
  lazily so off-screen rows don't compete for connections
- ENH: Plots use the canvas renderer in production; the SVG renderer built one
  DOM subtree per curve, which froze the page on analyses over large dataset
  collections. Plot downloads are PNG accordingly, and the menu entry says so
- ENH: Notifications are polled every 30 seconds instead of every second, and
  not at all from background tabs
- ENH: Task-status rows back off their polling from 5 to at most 30 seconds
  while a task runs; measurement cards poll every 3 seconds instead of every
  second
- MAINT: Database connections are reused across requests in production
  (`CONN_MAX_AGE`, env-overridable, with health checks) instead of reconnecting
  per request
- MAINT: Presigned storage URLs live for a day instead of an hour, so
  thumbnails and plot data on a page left open no longer break after an hour
- MAINT: The request profiler no longer records the notification poll, which
  inserted a profiling row per request without ever being the request under
  investigation
- BUG: Task-finished events are emitted from a watcher instead of a computed
  getter, and the "load more thumbnails" over-fetch (limit growing with offset)
  is gone

## 1.34.0 (2026-08-03)

- ENH: The dataset list shows one row per dataset, naming its version and offering
  the older ones, instead of a separate row per published version
- ENH: The Filters tab names the trend that detrending subtracted, i.e. the slope
  of the removed tilt and the radius of the removed curvature
- ENH: The "undefined data" badge of a measurement names how much of it is
  undefined
- ENH: The publish wizard states on its first step when a dataset cannot be
  published, listing the measurements that are not ready, instead of failing at the
  final "Publish" step
- ENH: The landing page of a published dataset now carries server-rendered metadata:
  a dataset-specific title and description, a schema.org JSON-LD description,
  citation meta tags and signposting typed links. Harvesters do not execute
  JavaScript, so anything they are meant to find has to be in the served HTML
- ENH: `robots.txt` points crawlers at the sitemap of published datasets, which is
  the only way they can be discovered: all links into the app are generated by
  JavaScript
- BUG: The BokehJS version loaded from the CDN is read from `package.json`, so it can
  no longer drift from the version the app is compiled against
- BUG: Task durations are shown as "42 sec" or "1 h 4 min" instead of the raw
  `0:00:42.123456` of the API, at a resolution that means something
- ENH: Reloading a dataset, measurement or contact-mechanics page returns to the tab
  that was open instead of the first one
- ENH: Power-spectral density plots carry a second axis above them showing the
  real-space size scale λ = 2π/q
- BUG: Task dashboard shows the username when a user has no name set
- BUG: The dataset list renders the "Page size" and "Sort by" controls again;
  `BInputGroup` was used without being imported, and this project registers
  bootstrap-vue-next components per file. Also corrected the casing of a closing
  `BTbody` tag in the properties table
- MAINT: Removed the npm dependencies that nothing imports, left over from when
  webpack still bundled BokehJS from source
- MAINT: Celery task time limits are now explicit and env-configurable
- MAINT: Added `TOPOBANK_ANALYSIS_MEMORY_*` settings for the analysis memory guard

## 1.33.0 (2026-08-02)

- ENH: Visual facelift: new analysis and dataset card style, tabs instead of pills,
  homogenized toolbars, less chrome
- ENH: Contextual help throughout the site
- ENH: User and tasks dashboard
- ENH: Token-based search
- ENH: Asynchronous ZIP downloads
- ENH: Citation recommendation for published datasets
- ENH: Reintroduced the supported file formats overview page
- ENH: Component versions shown in the user side panel, including
  `topobank-rest-api` and `topobank-orcid`
- ENH: Spinner while the site is loading
- BUG: Hardened settings and fixed backend and frontend audit findings
- BUG: Forward the CSRF token from the cookie on axios requests; fixed the
  topography delete URL
- BUG: Fixed the user search modal (wrong endpoint, paginated response)
- BUG: No spinner is shown when all tasks have failed
- BUG: Fixed error reporting and the version information in the offcanvas
- MAINT: The Django project configuration lives here now: `manage.py`, the
  `ce_ui.settings.*` modules, the root URL configuration and the WSGI/ASGI entry
  points moved over from `topobank`
- MAINT: Plugins are wired explicitly through `INSTALLED_APPS`; removed the old
  entry-point plugin system and plugin permissions
- MAINT: REST API split into `topobank-rest-api`; users, organizations and
  authorization into `topobank-orcid`; removed django-guardian
- MAINT: Reorganized the JS component structure; logic extracted into tested TS
  modules
- MAINT: Celery beat task for truncating the request profiler log
- MAINT: Refresh of Bokeh plots for visualization
- MAINT: Physical sizes are displayed without e-notation
- MAINT: `analysis_function` -> `workflow`
- MAINT: The changelog is no longer served as a static file; the component versions
  in the side panel link to the repositories where changelogs are published
- BUILD: Changed build system to hatchling
- BUILD: Load BokehJS from a prebuilt bundle instead of re-bundling it (#67)
- BUILD: Updated frontend dependencies (Bokeh 3.9, Pinia 4, OpenSeadragon 6,
  DataTables 3, bootstrap-vue-next 0.45)
- BUILD: Force-include the app's static files in the distribution; they were missing
  from the wheel because `.gitignore` matched `ce_ui/static/`
- BUILD: Anchored the `static/` pattern in `.gitignore` to the repository root

## 1.32.0 (2025-12-16)

- ENH: Dataset Collection view and publish UI
- ENH: Integrated TipTap rich text editor for dataset descriptions
- BUG: Re-enabled Description, Instrument and Filters tabs in topography detail view
- BUG: Fixed thumbnail alignment and sizing in dataset list on Firefox

## 1.31.2 (2025-08-19)

- BUG: Avoid error if _error is null

## 1.31.1 (2025-07-28)

- ENH: Button for creating zoomable image if missing

## 1.31.0 (2025-07-28)

- ENH: Badges that show number of measurements, properties and attachments
- ENH: Surface topography challenge homepage

## 1.30.6 (2025-04-23)

- ENH: Report publication errors

## 1.30.5 (2025-04-23)

- BUG: Reviewing accepted terms and conditions (#129)

## 1.30.4 (2025-04-04)

- BUG: Added missing template
- MAINT: Moved allauth route registration to CE-UI

## 1.30.3 (2025-04-02)

- BUG: Fixed upload of attachments (#107)
- BUG: Fixed user statistics
- BUG: Fixed missing names in selection view (#110)

## 1.30.2 (2025-03-18)

- MAINT: Show "Public datasets" when not logged in (#101)
- MAINT: Fixed example links

## 1.30.1 (2025-03-18)

- BUG: Fixed upload of measurements

## 1.30.0 (2025-03-17)

- ENH: New dataset list
- ENH: Search while typing
- ENH: New publication flow
- ENH: New topnav basket for selections
- ENH: Pinia store for selections
- BUG: Fixing UI for property deletion
- MAINT: Each page is now a single page application

## 1.11.2 (2025-03-04)

- BUG: Don't show publish button if user has no rights to publish (#84)
- BUG: Show bare task duration (#85)
- BUG: Select data channel if parsing file fails for a specific channel
- BUG: Show properties to the right of, not below, the thumbnail

## 1.11.1 (2025-03-04)

- MAINT: Show messages as toasts
- MAINT: Show errors as toasts
- MAINT: Prettified surface details card

## 1.11.0 (2025-03-03)

- ENH: Quickly switching to next measurement/topography (#94)
- BUG: Fixed measurement/topography download (#89)
- BUG: Don't leak DST name in 403 error (#75)
- BUG: Proper error message when DST is not accessible (#93)

## 1.10.1 (2025-02-11)

- BUG: Fix DOI badge
- MAINT: Renamed topography card "Properties" tab to "Details" to avoid
  confusion with surface properties

## 1.10.0 (2025-02-11)

- MAINT: Updated for API changes in topobank v1.55.0
- BUG: Update used icons to fontawesome 6
- BUG: Fix DOI link
- BUG: Raise permission error if object does not exist

## 1.9.4 (2024-12-05)

- BUG: Fix download of deep zoom images

## 1.9.3 (2024-11-27)

- BUG: Fixed user permission editor
- BUG: Fix retrieval of user information in permission management
- BUG: Fix hyperlinks in notifications
- BUG: Reporting proper error when DZI files are missing

## 1.9.2 (2024-11-25)

- BUG: Enable toast orchestrator for analysis app

## 1.9.1 (2024-11-13)

- BUG: Fixed reporting task progress
- BUG: Visualization app name was removed
- MAINT: Added prefix to DeepZoomImage component
- MAINT: Error reporting with toasts

## 1.9.0 (2024-11-13)

- ENH: Attachments for surfaces and topographies
- ENH: Rewritten notification and user panels
- MAINT: Removed outdated help page
- MAINT: Single Vue.js application for top navigation bar
- MAINT: Updated for latest topobank

## 1.8.4 (2024-05-14)

- BUG: Displaying plots with unspecified `xData` and `yData`

## 1.8.3 (2024-05-13)

- BUG: Fixed unit conversion in contact mechanics distributions plots

## 1.8.2 (2024-05-13)

- BUG: `task_progress` can be null
- BUG: Need to watch for changes in analysis status 

## 1.8.1 (2024-05-13)

- BUG: Screenshots are now JPG files, not PNG
- MAINT: Cosmetics on home screen text

## 1.8.0 (2024-05-12)

- MAINT: Simplified Vue components but introducing a parent `AnalysisCard`
  component, switching to the composition API throughout and making use of
  bootstrap-vue-next components

## 1.7.2 (2024-03-22)

- BUG: Fixed version discovery

## 1.7.1 (2024-03-21)

- MAINT: preventing property name duplications in editor
- BUILD: Changed build system to flit

## 1.7.0 (2024-03-12)

- ENH: Properties as key-value pairs with categorical and numerical values,
  including units
- BUG: Fix breadcrumb navigation when not logged in (#48)
- BUG: Fix redirect after deleting digital surface twin (#51)

## 1.6.1 (2024-01-30)

- MAINT: Cosmetic fixes to the user interface
- MAINT: Adding gitignore

## 1.6.0 (2024-01-22)

- ENH: Select search order
- ENH: Report creation date

## 1.5.1 (2024-01-21)

- ENH: Added alert for failing uploads
- BUG: Fixed search (#45)
- BUG: Fixed display of alerts
- MAINT: Nicer placeholders while loading dataset

## 1.5.0 (2024-01-20)

- MAINT: Split user interface module from main TopoBank
- MAINT: Fix Boostrap style on close button of modal windows
- MAINT: Reorganized layout of left control buttons
- MAINT: Enforcing PEP-8 style
