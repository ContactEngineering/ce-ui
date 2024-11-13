# Changelog for plugin *ce-ui*

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
