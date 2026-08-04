import path from "node:path";
import {defineConfig} from "vitest/config";

export default defineConfig({
    resolve: {
        alias: {
            "@": path.resolve(__dirname, "frontend")
        }
    },
    test: {
        environment: "node",
        include: ["frontend/**/*.test.ts"],
        coverage: {
            // Coverage is measured over the TypeScript logic modules. The
            // .vue single-file components are excluded: this config carries no
            // Vue plugin, so they cannot be instrumented here.
            include: ["frontend/**/*.ts"],
            exclude: ["frontend/**/*.test.ts"]
        }
    }
});
