const path = require('path');
const webpack = require('webpack');
const {VueLoaderPlugin} = require('vue-loader');

module.exports = {
    entry: {
        app: '@/app.ts'
    }, output: {
        path: path.resolve(__dirname, 'static/js'),
        filename: '[name].bundle.js',
        library: ['topobank', '[name]']
    }, module: {
        rules: [{
            test: /\.ts$/, use: [{
                loader: "ts-loader",
                options: {
                    appendTsSuffixTo: [/\.vue$/],
                    transpileOnly: true,
                },
            }], exclude: /node_modules/
        }, {
            test: /\.vue$/, loader: 'vue-loader', options: {
                loaders: {
                    js: 'babel-loader',
                }
            }, exclude: /node_modules/
        }, {
            test: /\.css$/,
            use: ['vue-style-loader', 'css-loader'],
            exclude: /node_modules/,
        }, {
            test: /\.s[ac]ss$/,
            use: ['vue-style-loader', 'css-loader', 'sass-loader'],
            exclude: /node_modules/,
        }]
    }, resolve: {
        alias: {
            topobank: path.resolve(__dirname, 'frontend'),
            "@": path.resolve(__dirname, 'frontend')
        }, extensions: ['.js', '.ts', '.scss', '.vue']
    }, plugins: [new VueLoaderPlugin()]
};
