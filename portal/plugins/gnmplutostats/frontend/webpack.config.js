var webpack = require('webpack');
var path = require('path');

var BUILD_DIR = path.resolve(__dirname + "/..", 'static/plutostats');
var APP_DIR = path.resolve(__dirname, 'app');

var config = {
    entry: APP_DIR + '/index.jsx',
    output: {
        path: BUILD_DIR,
        filename: 'frontend.js'
    },
    module : {
        rules : [
            {
                test : /\.jsx?/,
                include : APP_DIR,
                loader : 'babel-loader',
                options : {
                    "presets": [
                        "env",
                        "react",
                        "stage-0"
                    ],
                    "plugins": [
                        "transform-class-properties",
                        "transform-decorators",
                        "transform-react-constant-elements",
                        "transform-react-inline-elements"
                    ]
                }
            },
            {
                test: /\.css$/,
                use: ['style-loader', 'css-loader']
            }
        ]
    }
};

module.exports = config;