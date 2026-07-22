const path = require("path");
const webpack = require("webpack");
const { VueLoaderPlugin } = require("vue-loader");

module.exports = env => {
    return {
        entry: {
            app: "@/app.ts"
        }, output: {
            path: env.prefix ? path.resolve(__dirname, env.prefix, "static/js") : path.resolve(__dirname, "static/js"),
            filename: "[name].bundle.js",
            library: ["topobank", "[name]"]
        }, module: {
            rules: [{
                // Transpile-only TS -> JS via esbuild (no type-checking, and no
                // dependency on the TypeScript compiler JS API, which the native
                // TypeScript 7 package no longer exposes). VueLoaderPlugin clones
                // this rule to also handle <script lang="ts"> blocks in .vue SFCs.
                test: /\.ts$/, loader: "esbuild-loader", options: {
                    loader: "ts", target: "es2020"
                }, exclude: /node_modules/
            }, {
                test: /\.vue$/, loader: "vue-loader", options: {
                    loaders: {
                        js: "babel-loader"
                    }
                }, exclude: /node_modules/
            }, {
                test: /\.css$/,
                use: ["vue-style-loader", "css-loader"],
                exclude: /node_modules/
            }, {
                test: /\.s[ac]ss$/,
                use: ["vue-style-loader", "css-loader", "sass-loader"],
                exclude: /node_modules/
            }]
        }, resolve: {
            alias: {
                topobank: path.resolve(__dirname, "frontend"),
                "@": path.resolve(__dirname, "frontend")
            }, extensions: [".js", ".ts", ".scss", ".vue"]
        }, externals: {
            // Do not bundle BokehJS. Webpack re-transpiling the @bokeh/bokehjs
            // source breaks it for Bokeh >= 3.1.0 (class-field init order); use
            // the prebuilt bundle exposed as the global `Bokeh` instead. The
            // matching bokeh-*.min.js scripts are loaded in app.html.
            "@bokeh/bokehjs": "Bokeh"
        }, plugins: [
            new VueLoaderPlugin(),
            new webpack.DefinePlugin({
                __VUE_OPTIONS_API__: JSON.stringify(true),
                __VUE_PROD_DEVTOOLS__: JSON.stringify(false),
                __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: JSON.stringify(false)
            })
        ]
    };
};
