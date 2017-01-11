# How to recompile CSS and JS

## CSS
CSS is written with SASS preprocessor so after you fix `dental_chart.scss` you should recompile it by runnning `sassc -t nested dental_chart.scss dental_chart.css`

## JS
To convert .js to IE-compliant JavaScript install babel:
```npm install babel babel-polyfill babel-preset-es2015-without-strict ```
and run:
```node_modules/.bin/babel --presets es2015-without-strict  dental_chart.es6.js --out-file dental_chart.js```
