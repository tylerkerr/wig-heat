(function(d3, fc) {
    'use strict';

//************************************************************
// Set up variables
//************************************************************

    // config references
    var chartConfig = {
        title : 'Line chart with toggle legend',
        target : 'chart-id',
        dataUrl : 'pseudo_data.json',
        updateVars : {}
    };

    // access the keys from data
    var dataKeys = [];

    // varibles used for updates
    var updateVars = fc.utilities.defaultConfig().updateVars;
    // create container var for different line series
    var lineSeriesArray = updateVars.lineSeriesArray;
    
    // create an alt array of dataKeys for updating yScale via legend
    var dataKeysUser = updateVars.dataKeysUser; // undefined

    // helper function to splice array
    function arraySplice(_array, _string) {
        var i = _array.indexOf(_string);
        if (i != -1) {
            _array.splice(i, 1);
        }
    }

    
// -----------------------------  

    function updateUrl() {
        return chartConfig.dataUrl;
    }

// -----------------------------
    
    // instantiate data config  
    var data = fc.utilities.dataConfig(),
        parseDate = d3.time.format('%Y-%m-%d').parse,
        formatDate = d3.time.format("%H:%M:%S");

// -----------------------------

    // select chart container(s)
    var chart = d3.select('#' + chartConfig.target);

// -----------------------------

    // set chart title
    function chartTitle() {
        var title = d3.select('#chart-title');

        title.text(chartConfig.title);
    }

// -----------------------------
    
    // id for spin loader
    var target = document.getElementById(chartConfig.target);


//************************************************************
// JSON callback
//************************************************************
 
    function init(dataUrl, variables) {

        // trigger loader unless already active
        if (d3.select('.spinner').empty()) {
            var spinner = new Spinner(opts).spin(target);
        }

        // load json data and trigger callback
        data.loadJson(dataUrl, function(data) {

            // access keys (except date) for legend and yScale extent
            dataKeys = d3.keys(data.data[0]).filter(function(d) { return d !== 'date'; }).sort(d3.ascending);

            // instantiate functions within callback
            dataFormat(data.data);
            chartTitle();
            lineChart(data.data);
            renderLegend(data.data);
        
            // stop the loader
            if (!d3.select('.spinner').empty()) {
                spinner.stop();
            }
            

        });
    } 

    init(updateUrl(), updateVars);

//************************************************************
// Clean/format data
//************************************************************

    function dataFormat(data) {
        data.forEach(function(d) {
            d.date = parseDate(d.date);
            
            for (var i = 0; i < dataKeys.length; i++) {
                // ensure numeric value
                d[dataKeys[i]] = +d[dataKeys[i]];
                // set zero for missing data
                if (isNaN(d[dataKeys[i]])) {
                    d[dataKeys[i]] = 0;
                }
            }  
        });
    }

//************************************************************
// Line chart
//************************************************************  

    function lineChart(data) {

        // check if dataKeysUser is empty or undefined
        if (!_.isArray(dataKeysUser) || _.isEmpty(dataKeysUser) ) {
            dataKeysUser = [];
            dataKeysUser = dataKeysUser.concat(dataKeys);
        } 

        var chartLayout = fc.utilities.chartLayout();

        chartLayout
            .marginLeft(60)
            .marginRight(20)
            .marginBottom(180);

        var chartBuilder = fc.utilities.chartBuilder(chartLayout);

        chart
            .call(chartBuilder);    


    // -----------------------------
        // Create scale for x axis
        var xScale = d3.time.scale()
            .domain(d3.extent(data, function(d) { return d.date; }))
            .range([0, chartLayout.getPlotAreaWidth()])
            .nice();
         
        // create scale for left y axis
        var yScale = d3.scale.linear()
            .domain(fc.utilities.extent(data, dataKeysUser))
            .range([chartLayout.getPlotAreaHeight(), 0])
            .nice();


    // -----------------------------
        // ensure locale time for x axis using moment.js
        var timeFormatter = function(date) {
            return moment(date).format("LT");
        };

        // create the axes
        var xAxis = d3.svg.axis()
            .scale(xScale)
            .orient('bottom')
            .tickPadding(8)
            .ticks(d3.time.minutes, 10)
            .tickFormat(timeFormatter);

        var yAxis = d3.svg.axis()
            .scale(yScale)
            .orient('left')
            .tickPadding(8)
            .ticks(9);

        function minorTicks() {
            d3.selectAll('.minor').remove();

            this.selectAll('svg .bottom line').data(xScale.ticks(d3.time.minutes), function(d) { return d; })
            .enter()
            .append('line')
            .attr('class', 'minor')
            .attr('y1', 0)
            .attr('y2', 5)
            .attr('x1', xScale)
            .attr('x2', xScale);
        }

        // add minor ticks to chart
        chartLayout.getAxisContainer('bottom')
            .call(minorTicks);

    // -----------------------------
       
        // create line series
        // create 'empty' array
        var lineSeriesArray = d3.range(dataKeys.length);
        // loop through to store the variable containers to create each line 
        for (var i = 0; i <= dataKeys.length; i++) {

            lineSeriesArray[i] = newLine(i+1);

        }
        // function to call required component code
        function newLine(i) {
            return fc.series.lineMultiple()
                .xValue(function(d) { return d.date; })
                .yValue(function(d) { return d[dataKeys[i-1]]; })
                .lineColour(i) 
                .xScale(xScale)
                .yScale(yScale);
        }


    // -----------------------------
        // add the components to the chart
        chartBuilder.setAxis('bottom', xAxis);
        chartBuilder.setAxis('left', yAxis);
        chartBuilder.addToPlotArea(lineSeriesArray);


    // -----------------------------
        // associate the data
        chartBuilder.setData(data);
        // draw  
        chartBuilder.render();


    // -----------------------------
       
    }

//************************************************************
// Legend
//************************************************************ 
    
    function renderLegend(data) {

        // create legend
        var legend = fc.tools.legend()
            .dataKeys(dataKeys)
            .dataKeysUser(dataKeysUser)
            .lineReferences(lineSeriesArray);

        // event to update yScale when toggling line series
        legend.on('toggleLegend', function(d, i) { 

            // console.log('toggleLegend: ' + d, i); 

            var line = d3.select('.line-' + (i+1)); // just adding one to the zero index of the array
            var lineId = d.replace(/\s+/g, '-').toLowerCase();

            // toggle item in array
            if (!_.contains(dataKeysUser, d)) {
                dataKeysUser.push(d);

                line
                    .style('opacity', 1)
                    .classed('legend-active', false);

                d3.select('#' + lineId).style('opacity', 1);

            } else if (_.contains(dataKeysUser, d) && dataKeysUser.length > 1) {
                arraySplice(dataKeysUser, d);
                
                line
                    .style('opacity', 0.2)
                    .classed('legend-active', true);

                d3.select('#' + lineId).style('opacity', 0.2);
            }

            // render updated chart view
            updateChart();

        });

        // Add the legend
        d3.select('#legend-list')
            .call(legend);


    }
 

// -----------------------------

    function updateChart() {
        init(updateUrl(), updateVars);
    }
    // listener for window resize
    window.addEventListener('resize', updateChart);


})(d3, fc);