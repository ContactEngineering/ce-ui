import {readdirSync, readFileSync, statSync} from "node:fs";
import path from "node:path";

import {describe, expect, it} from "vitest";

/* BNavItem renders an <li> around a link and does not keep attributes off
   that <li>. A `class="btn ..."` therefore styles the <li>, while clicks and
   `disabled` belong to the inner link: clicks on the visible button's padding
   are lost, and a disabled button still looks enabled (topobank#1407). Use
   BButton for anything that should look like a button. */

const FRONTEND = path.resolve(__dirname, "..");

function vueFiles(dir: string): string[] {
    return readdirSync(dir).flatMap(name => {
        const full = path.join(dir, name);
        if (statSync(full).isDirectory()) {
            return name === "node_modules" ? [] : vueFiles(full);
        }
        return name.endsWith(".vue") ? [full] : [];
    });
}

describe("BNavItem", () => {
    it("is never styled as a button", () => {
        const offenders = vueFiles(FRONTEND).flatMap(file => {
            const source = readFileSync(file, "utf-8");
            // Opening tags, which may span several lines and contain ">" inside
            // quoted attribute values (e.g. v-if="n > 1")
            const tags = source.match(/<BNavItem\b(?:[^>"']|"[^"]*"|'[^']*')*>/g) ?? [];
            return tags
                .filter(tag => /\sclass="[^"]*\bbtn\b/.test(tag))
                .map(tag => `${path.relative(FRONTEND, file)}: ${tag.replace(/\s+/g, " ")}`);
        });
        expect(offenders).toEqual([]);
    });
});
