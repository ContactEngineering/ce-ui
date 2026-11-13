# Changelog for plugin *ce-ui*

<!--
Style for this changelog (keep to it so entries stay uniform):

- Newest version first. Heading `vX.Y.Z (DDMonYY)`, underlined with dashes.
  A version not yet released is headed `vX.Y.Z (not yet released)`.
- One bullet per user-visible change, at most two lines (about 200
  characters). Say what changed for the user and, if useful, why or by how
  much. Omit internals: no function, class, file or variable names, no
  environment variables, no commit or PR references.
- Start every bullet with one of: `ENH:` (new feature), `BUG:` (fix),
  `API:` (interface change), `PERF:` (speed or memory), `MAINT:`, `TST:`,
  `DOC:`, `BUILD:`, `CI:`.
- Small related fixes may share one bullet. No trailing period on bullets.
-->

v1.39.0 (not yet released)
--------------------------

- ENH: Accounts can only be created with an ORCID iD, which cannot be
  disconnected later; other sign-up attempts land on a page explaining this
- ENH: Sign in with Google or with an email address and password, in addition
  to ORCID; the sign-in page offers every provider the deployment configured
- ENH: Google sign-in connects to an existing account with the same address
  only if it was confirmed, so an unconfirmed claim cannot capture a sign-in
- ENH: Users are emailed when a password, email address or connected identity
  changes, saying where it came from and what to do if it was not them
- ENH: Account emails (confirmation, password reset) are written and styled
  for contact.engineering, with a branded HTML part alongside the plain text
- BUG: Account email subjects no longer start with a placeholder site name
  ("example.com") on deployments that never edited it
- ENH: Connecting an identity provider adds the addresses it has verified, so
  a Google account brings its address and no confirmation email is needed
- ENH: New connected identities page, linked from the user menu and profile,
  to list, connect and disconnect the ways of signing in
- ENH: Warn when an account has no confirmed email address, which leaves it
  without Google or password sign-in and no way to recover access
- ENH: Publishing a dataset or collection requires a connected ORCID iD,
  enforced for API clients too and explained up front on the publish pages
- ENH: Power spectral density and RMS height cards can overlay reference data
  from the Surface-Topography Challenge study, behind an optional toggle
- ENH: Individual plot lines can have a fixed color and dash style and can
  hide their point markers, independently of the rest of the plot
- BUG: Fixed a landing page test that failed for two hours a day because of
  a timezone mismatch in the citation date
- DOC: New guide to how users sign in and how to obtain credentials for each
  identity provider, including the Google consent screen setup
- MAINT: The user, permission and organization apps were folded into this
  package; existing databases need no migration and custom models still work

v1.38.0 (04Aug26)
-----------------

- PERF: Analysis cards poll all pending analyses in one request instead of one
  per analysis, so large datasets no longer flood the server with traffic
- PERF: Opening a card's task list fetches the workflow description once
  instead of once per row

v1.37.0 (04Aug26)
-----------------

- PERF: The dataset detail page needs a handful of database queries instead of
  about ten per measurement and paints at once; measurement cards load later
- PERF: Publication details of a published dataset arrive with the dataset
  instead of needing a separate request before anything renders
- MAINT: The permissions tab grants and revokes individual permissions instead
  of rewriting the whole list
- BUG: Tag badges in the dataset detail sidebar were empty

v1.36.0 (04Aug26)
-----------------

- PERF: Each page of the dataset list loads in one request, with creators,
  publication details and thumbnails included, instead of two or three per row
- PERF: Links to thumbnails, plot data and zoomable images stay the same
  between page loads, so browsers serve them from their cache
- BUG: The "Created by you" and "shared with you" badges on dataset rows work
  again

v1.35.0 (04Aug26)
-----------------

- PERF: Analysis cards refresh at most every ten seconds while tasks run, plus
  once at the end, instead of rebuilding fully after every finished task
- PERF: The dataset list draws thumbnails from data it already has, and
  loads them lazily so off-screen rows don't compete for connections
- PERF: Plots render to canvas, which no longer freezes the page for analyses
  of large collections; plot downloads are now PNG files
- PERF: Notifications are checked every 30 seconds instead of every second,
  and not at all from background tabs
- PERF: Running tasks are polled less often, backing off from 5 to 30 seconds;
  measurement cards poll every 3 seconds instead of every second
- PERF: Database connections are reused across requests in production instead
  of reconnecting each time
- BUG: Thumbnails and plot data on a page left open no longer break after an
  hour; storage links now last a day
- MAINT: The request profiler no longer records the notification check
- BUG: Fixed unreliable task-finished updates and over-fetching when loading
  more thumbnails

v1.34.0 (03Aug26)
-----------------

- ENH: The dataset list shows one row per dataset, naming its version and
  offering older ones, instead of one row per published version
- ENH: The Filters tab names the slope and curvature radius that detrending
  removed
- ENH: The "undefined data" badge of a measurement says how much of it is
  undefined
- ENH: The publish wizard says on its first step when a dataset cannot be
  published and which measurements are not ready
- ENH: Published dataset pages carry metadata for search engines and citation
  harvesters in the served HTML: title, description, structured data, links
- ENH: Search engines are pointed at a sitemap of published datasets, the only
  way they can discover them
- BUG: The plotting library loaded at runtime always matches the version the
  app was built against
- BUG: Task durations read "42 sec" or "1 h 4 min" instead of a raw
  timestamp with microseconds
- ENH: Reloading a dataset, measurement or contact mechanics page returns to
  the tab that was open
- ENH: Power spectral density plots show the real-space size scale on a second
  axis above the plot
- BUG: The task dashboard shows the username when a user has no name set
- BUG: The page size and sort controls of the dataset list are shown again;
  fixed a markup error in the properties table
- MAINT: Removed unused frontend dependencies
- MAINT: Background task time limits are explicit and configurable
- MAINT: Added settings for the memory guard of analyses

v1.33.0 (02Aug26)
-----------------

- ENH: Visual facelift: new analysis and dataset card style, tabs instead of
  pills, uniform toolbars, less chrome
- ENH: Contextual help throughout the site
- ENH: User and task dashboards
- ENH: Token-based search
- ENH: ZIP downloads are prepared in the background
- ENH: Citation recommendation for published datasets
- ENH: The overview of supported file formats is back
- ENH: The user side panel shows the versions of all installed components
- ENH: A spinner is shown while the site is loading
- BUG: Hardened the security settings and fixed issues found in a code audit
- BUG: Requests carry the security token correctly again; fixed deleting a
  measurement
- BUG: Fixed the user search dialog
- BUG: No spinner is shown when all tasks have failed
- BUG: Fixed error reporting and the version information in the side panel
- MAINT: The Django project configuration, including the management entry
  point, settings and URL configuration, moved here from topobank
- MAINT: Plugins are enabled explicitly in the settings; removed the old plugin
  discovery and plugin permissions
- MAINT: The REST API and the user and organization management moved to
  separate packages; removed the per-object permission library
- MAINT: Reorganized the frontend code and moved logic into tested modules
- MAINT: The request profiler log is truncated periodically
- MAINT: Refreshed the plots used for visualization
- MAINT: Physical sizes are shown without exponential notation
- MAINT: Analysis functions are now called workflows
- MAINT: The changelog is no longer served by the app; the component versions
  in the side panel link to the repositories that publish the changelogs
- BUILD: Changed build system to hatchling
- BUILD: The plotting library is loaded from a prebuilt bundle instead of being
  bundled again
- BUILD: Updated frontend dependencies (Bokeh 3.9, Pinia 4, OpenSeadragon 6,
  DataTables 3, bootstrap-vue-next 0.45)
- BUILD: The app's static files are included in the wheel again; an ignore
  pattern had excluded them

v1.32.0 (16Dec25)
-----------------

- ENH: Dataset collection view and publish workflow
- ENH: Rich text editor for dataset descriptions
- BUG: The description, instrument and filters tabs of the measurement view are
  back
- BUG: Fixed thumbnail alignment and size in the dataset list on Firefox

v1.31.2 (19Aug25)
-----------------

- BUG: Fixed an error in the dataset description editor when no error was set

v1.31.1 (28Jul25)
-----------------

- ENH: Button to create a zoomable image if it is missing

v1.31.0 (28Jul25)
-----------------

- ENH: Badges show the number of measurements, properties and attachments
- ENH: Homepage for the Surface-Topography Challenge

v1.30.6 (23Apr25)
-----------------

- ENH: Publication errors are reported

v1.30.5 (23Apr25)
-----------------

- BUG: Fixed reviewing accepted terms and conditions

v1.30.4 (04Apr25)
-----------------

- BUG: Added a missing page template
- MAINT: The account pages are now set up by this package

v1.30.3 (02Apr25)
-----------------

- BUG: Fixed uploading attachments
- BUG: Fixed user statistics
- BUG: Fixed missing names in the selection view

v1.30.2 (18Mar25)
-----------------

- MAINT: Show "Public datasets" when not logged in
- MAINT: Fixed example links

v1.30.1 (18Mar25)
-----------------

- BUG: Fixed uploading measurements

v1.30.0 (17Mar25)
-----------------

- ENH: New dataset list
- ENH: Search while typing
- ENH: New publication workflow
- ENH: Selections are collected in a basket in the top navigation bar and kept
  across pages
- BUG: Fixed the interface for deleting properties
- MAINT: Each page is now a single-page application

v1.11.2 (04Mar25)
-----------------

- BUG: The publish button is hidden from users without the right to publish
- BUG: Show the bare task duration
- BUG: Select a data channel if reading a file fails for a specific channel
- BUG: Show properties to the right of the thumbnail, not below it

v1.11.1 (04Mar25)
-----------------

- MAINT: Messages and errors are shown as toasts
- MAINT: Prettified the dataset details card

v1.11.0 (03Mar25)
-----------------

- ENH: Quickly switch to the next measurement
- BUG: Fixed downloading measurements
- BUG: Error pages no longer reveal the name of an inaccessible dataset, and
  show a proper message instead

v1.10.1 (11Feb25)
-----------------

- BUG: Fixed the DOI badge
- MAINT: Renamed the "Properties" tab of the measurement card to "Details" to
  avoid confusion with dataset properties

v1.10.0 (11Feb25)
-----------------

- MAINT: Updated for interface changes in topobank v1.55.0
- BUG: Updated icons to Font Awesome 6
- BUG: Fixed the DOI link
- BUG: A missing object raises a permission error

v1.9.4 (05Dec24)
----------------

- BUG: Fixed downloading zoomable images

v1.9.3 (27Nov24)
----------------

- BUG: Fixed the user permission editor and loading user information in it
- BUG: Fixed links in notifications
- BUG: A proper error is reported when zoomable image files are missing

v1.9.2 (25Nov24)
----------------

- BUG: Toast messages are shown in the analysis app

v1.9.1 (13Nov24)
----------------

- BUG: Fixed reporting of task progress
- BUG: Fixed the analysis result page, which broke after an internal rename
- MAINT: Errors are reported as toasts

v1.9.0 (13Nov24)
----------------

- ENH: Attachments for datasets and measurements
- ENH: Rewritten notification and user panels
- MAINT: Removed the outdated help page
- MAINT: The top navigation bar is a single application
- MAINT: Updated for the latest topobank

v1.8.4 (14May24)
----------------

- BUG: Plots display even when a data series does not say which columns hold
  its x and y values

v1.8.3 (13May24)
----------------

- BUG: Fixed unit conversion in the contact mechanics distribution plots

v1.8.2 (13May24)
----------------

- BUG: Analyses that report no task progress no longer cause an error
- BUG: Changes in analysis status are picked up

v1.8.1 (13May24)
----------------

- BUG: Screenshots are now JPG files, not PNG
- MAINT: Cosmetic changes to the home page text

v1.8.0 (12May24)
----------------

- MAINT: Simplified the analysis cards by giving them a common base and
  modernizing the frontend code throughout

v1.7.2 (22Mar24)
----------------

- BUG: Fixed version discovery

v1.7.1 (21Mar24)
----------------

- MAINT: The property editor prevents duplicate property names
- BUILD: Changed build system to flit

v1.7.0 (12Mar24)
----------------

- ENH: Properties as key-value pairs with categorical or numerical values,
  including units
- BUG: Fixed breadcrumb navigation when not logged in
- BUG: Fixed the redirect after deleting a dataset

v1.6.1 (30Jan24)
----------------

- MAINT: Cosmetic fixes to the user interface

v1.6.0 (22Jan24)
----------------

- ENH: Select the sort order of search results
- ENH: Show the creation date

v1.5.1 (21Jan24)
----------------

- ENH: An alert is shown when an upload fails
- BUG: Fixed search
- BUG: Fixed the display of alerts
- MAINT: Nicer placeholders while a dataset loads

v1.5.0 (20Jan24)
----------------

- MAINT: The user interface was split out of the main TopoBank package
- MAINT: Fixed the Bootstrap style of the close button in dialogs
- MAINT: Reorganized the control buttons on the left
- MAINT: The Python code follows the PEP 8 style
