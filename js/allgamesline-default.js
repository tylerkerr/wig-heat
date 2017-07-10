(function(d3, fc) {
    'use strict';

    fc.utilities.defaultConfig = function() {

        var config = {};
            
        var chartId = 'chart-id';

        config.colourArray = ['#d62728' , '#1f77b4', '#2ca02c', '#ff7f0e', '#9467bd', ' #8c564b', '#7f7f7f', '#bcbd22', '#17becf', '#e377c2'];

        // add colour range based on  d3.scale.category10()
        config.colours = d3.scale.ordinal()
          .domain(['red', 'blue', 'green', 'orange', 'purple', 'brown', 'grey', 'lime', 'java', 'orchid'])
          .range(config.colourArray);

        // set locale time using [moment.js](http://momentjs.com/docs/#/customization/long-date-formats/) 
        moment.locale('en', {
            longDateFormat : {
                LT: "h:mm",
                LTS: "h:mm:ss A",
                L: "MM/DD/YYYY",
                LL: "MMMM Do YYYY",
                LLL: "MMMM Do YYYY LT",
                LLLL: "dddd, MMMM Do YYYY LT"
            }
        });

        // update object
        config.updateVars = {};


        config.chartId = function(value) {
            if (!arguments.length) return chartId;
            chartId = value;
            return this;
        };

        return config;
    
    };


}(d3, fc));
