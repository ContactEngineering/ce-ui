// Build the stylesheet for the server-rendered Django pages.
//
// The Vue app gets its styling from the bundle, which injects the compiled
// theme at runtime. Pages rendered by Django alone -- sign-in, connected
// identities, the whole account section -- never load that bundle, so without
// this they would fall back to whatever `base.html` links, and look like a
// different site. This compiles the same theme into a plain stylesheet that
// `base.html` can link, and puts the fonts it references where the compiled
// URLs point.
//
// Run via `npm run build-css`.

import { readFileSync, writeFileSync, mkdirSync, copyFileSync, existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import * as sass from "sass";

const root = dirname(fileURLToPath(import.meta.url));
const entry = join(root, "frontend/scss/standalone.scss");
// The app's own static directory, rather than the one webpack writes to: this
// is an asset the Django templates need, so it should be found wherever the
// app is installed -- in development without depending on the extra static
// directory the devbox shell configures, and in production via collectstatic.
const outDir = join(root, "ce_ui/static/css");
const outFile = join(outDir, "theme.css");

const result = sass.compile(entry, {
    loadPaths: [join(root, "node_modules")],
    style: "compressed",
    // The theme still uses `@import`, which Dart Sass deprecates in favour of
    // `@use`. Migrating it is a separate job; silence the noise until then.
    silenceDeprecations: ["import", "global-builtin", "color-functions", "if-function"],
});

mkdirSync(outDir, { recursive: true });
writeFileSync(outFile, result.css);

// Copy exactly the font files the compiled stylesheet asks for, resolving each
// relative URL back to the package it came from. Deriving the list from the CSS
// keeps the two in step: change a weight in `standalone.scss` and the right
// files follow, with no list to update here.
function sourceFor(url) {
    // FontAwesome: `../webfonts/fa-solid-900.woff2`
    let match = url.match(/^\.\.\/webfonts\/(.+)$/);
    if (match) {
        return join(root, "node_modules/@fortawesome/fontawesome-free/webfonts", match[1]);
    }
    // Fontsource: `./files/ibm-plex-sans-latin-400-normal.woff2`, whose package
    // name is the part of the filename before the subset.
    match = url.match(/^\.\/files\/(([a-z0-9-]+?)-[a-z]+-\d+-[a-z]+\..+)$/);
    if (match) {
        return join(root, "node_modules/@fontsource", match[2], "files", match[1]);
    }
    return null;
}

const urls = new Set(
    [...result.css.toString().matchAll(/url\((\.\.?\/[^)]+)\)/g)].map((m) => m[1])
);

let copied = 0;
const missing = [];
for (const url of urls) {
    const from = sourceFor(url);
    if (from === null || !existsSync(from)) {
        missing.push(url);
        continue;
    }
    const to = resolve(outDir, url);
    mkdirSync(dirname(to), { recursive: true });
    copyFileSync(from, to);
    copied += 1;
}

if (missing.length > 0) {
    // A referenced font that cannot be found would 404 at runtime and silently
    // fall back to a system face, so fail the build instead.
    console.error(`build-css: cannot resolve ${missing.length} font reference(s):`);
    for (const url of missing) console.error(`  ${url}`);
    process.exit(1);
}

const kb = (n) => `${Math.round(n / 1024)} kB`;
console.log(`build-css: ${outFile} (${kb(readFileSync(outFile).length)}), ${copied} font files`);
