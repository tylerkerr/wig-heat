(function(d3, fc) {
    'use strict';

    fc.utilities.dataConfig = function() {

        var config = {},
            dispatch = d3.dispatch('dataReady', 'dataLoading'),
            data;


        var chartId = fc.utilities.defaultConfig().chartId;

        // create a method to load json file, and a callback on response
        config.loadJson = function(_file, _callback) {

            // load json file using d3.json.
            d3.json(_file, function (_err, _data) {
                //Execute the callback, assign the data to the context.

                // produce error if JSON load fails
                if (_data) { 
                    console.log('data loaded');
                } else if  (_err) { 

                  var errorMsg = d3.select('#error');

                  if (errorMsg.empty()) {

                    var errorMsg = d3.select('.chart')
                        .append('h3')
                        .attr('id', 'error')
                        .style("opacity", 0)
                        .html('! Error loading chart data ');
                    errorMsg.transition()
                        .style("opacity", 1);
                  }

                  return console.warn(_err);   
                }


                _callback(_data);

             
            });


        };

        d3.rebind(config, dispatch, 'on');

        config.chartId = function(value) {
            if (!arguments.length) return chartId;
            chartId = value;
            return this;
        };

        return config;


    
    };


}(d3, fc));
