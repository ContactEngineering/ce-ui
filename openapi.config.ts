import { defineConfig } from '@hey-api/openapi-ts';

// TypeScript types.gen.ts are generated based this config file
// export configuration can be found here: https://heyapi.dev/openapi-ts/output/typescript
export default defineConfig({
    //input: 'https://api.surface.design/api/schema/',
    input: 'http://localhost:8000/api/schema/',
    output: {
        format: 'prettier',
        path: 'frontend/api',
    },
    plugins: ['@hey-api/client-axios'],
});
