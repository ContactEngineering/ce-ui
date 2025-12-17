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
                test: /\.ts$/, use: [{
                    loader: "ts-loader", options: {
                        appendTsSuffixTo: [/\.vue$/], transpileOnly: true
                    }
                }], exclude: /node_modules/
            }, {
                test: /\.vue$/, loader: "vue-loader", options: {
                    loaders: {
                        js: "babel-loader"
                    }
                }, exclude: /node_modules/
            }, {
                // CSS files (including Quasar, Font Awesome, etc.)
                test: /\.css$/,
                use: ["vue-style-loader", "css-loader"]
            }, {
                // SASS/SCSS files
                test: /\.s[ac]ss$/,
                use: ["vue-style-loader", "css-loader", "sass-loader"]
            }, {
                // Font files (for Quasar icons)
                test: /\.(woff|woff2|eot|ttf|otf)$/,
                type: 'asset/resource'
            }]
        }, resolve: {
            alias: {
                topobank: path.resolve(__dirname, "frontend"),
                "@": path.resolve(__dirname, "frontend")
            }, extensions: [".js", ".ts", ".scss", ".vue"]
        }, plugins: [
            new VueLoaderPlugin(),
            // Vue feature flags to suppress warnings
            new webpack.DefinePlugin({
                __VUE_OPTIONS_API__: true,
                __VUE_PROD_DEVTOOLS__: false,
                __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: false
            })
        ]
    };
};
