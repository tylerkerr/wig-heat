(function(d3, fc) {
    'use strict';

    fc.tools.legend = function() {

        var container = 'legend-html', // id
            list = 'legend-list', // id references 
            dataKeys = [], // array of key values from json object data
            lineReferences = [], // array for line series variables
            // 
            dataKeysUser = []; // updated keys for yScale extent

        var dispatch = d3.dispatch('toggleLegend');


        var legend = function() {

            // ensure container is visible 
            d3.select('#' + container).transition().duration(1000).style('opacity', 1);

            var legend = d3.select('#' + container + ' ul');
            // create legend container if doesn't exist
            if (legend.empty()) {
                legend = d3.select('#' + container)
                    .attr('class', 'pure-menu pure-menu-horizontal');
                // legend
                //     .append('span')
                //     .attr('class', 'pure-menu-heading')
                //     .text('LEGEND:');
                legend
                    .append('ul')
                    .attr('class', 'pure-menu-list')
                    .attr('id', list);
            
                // add the legend items
                var legendList = d3.select('#' + list)
                    .selectAll('li')
                    .data(dataKeys);

                legendList   
                    .enter()
                    .append('li')
                    .attr('class', 'pure-menu-item legend-item')
                    .attr('id', function(d) {
                        // any spaces replaced with dashes and all letters converted to lowercase
                        return d.replace(/\s+/g, '-').toLowerCase();
                    })
                    .on('click', function(d,i) {  
                        return dispatch.toggleLegend(d, i); 
                    });

                legendList.append('span')
                    .attr('class', 'legend-line')
                    .style('color', function(d,i) { return fc.utilities.defaultConfig().colourArray[i]; })
                    .html(' &mdash;');

                legendList.append('span')
                    .attr('class', 'legend-title')
                    .style('color', '#454545')   
                    .html(function(d) { return d; });
            }
        };


       legend.container = function(value) {
            if (!arguments.length) return container;
            container = value;
            return this;
        };

        legend.list = function(value) {
            if (!arguments.length) return list;
            list = value;
            return this;
        };

        legend.dataKeys = function(value) {
            if (!arguments.length) return dataKeys;
            dataKeys = value;
            return this;
        };

        legend.dataKeysUser = function(value) {
            if (!arguments.length) return dataKeysUser;
            dataKeysUser = value;
            return this;
        };

        legend.lineReferences = function(value) {
            if (!arguments.length) return lineReferences;
            lineReferences = value;
            return this;
        };

        d3.rebind(legend, dispatch, 'on');

        return legend;
    };

}(d3, fc));
