$(function () {
  var margin = { top: 50, right: 0, bottom: 100, left: 30 },
    width = 1230 - margin.left - margin.right,
    height = 800 - margin.top - margin.bottom,
    gridSize = Math.floor(height / 24),
    legendElementWidth = gridSize * 3.11,
    buckets = 9,
    // colors = ["#ffffd9","#edf8b1","#c7e9b4","#7fcdbb","#41b6c4","#1d91c0","#225ea8","#253494","#081d58"], // alternatively colorbrewer.YlGnBu[9]
    // colors = ["#f7feff", "#e6fffd", "#dcffd5", "#caff76", "#fff600", "#ffd200", "#ffa200", "#ff7200", "#ff0000"], // alternatively colorbrewer.YlGnBu[9]
    colors = ["#ffffff", "#fefefe", "#fefdfd", "#fefcfc", "#fefcfb", "#fefbfa", "#fefbf9", "#fefaf9", "#fefaf8", "#fefaf7", "#fefaf6", "#fefaf5", "#fefaf4", "#fefaf3", "#fefaf2", "#fdfbf1", "#fdfbf0", "#fdfcef", "#fdfdee", "#fdfded", "#fcfdec", "#fbfdeb", "#fafdeb", "#f9fdea", "#f8fde9", "#f6fde8", "#f5fde7", "#f4fde6", "#f2fde6", "#f0fde5", "#effce4", "#edfce3", "#ebfce2", "#e9fce1", "#e8fce1", "#e5fce0", "#e3fcdf", "#e1fcde", "#dffcdd", "#ddfcdc", "#dcfcdd", "#dbfcde", "#dafcdf", "#d9fce0", "#d8fce1", "#d8fce2", "#d7fbe3", "#d6fbe4", "#d5fbe6", "#d4fbe7", "#d3fbe8", "#d3fbea", "#d2fbec", "#d1fbed", "#d0fbef", "#cffbf1", "#cffbf3", "#cefbf5", "#cdfbf7", "#ccfbf9", "#cbfafb", '#caf7fa','#c8f5fa','#c5f2fa','#c2effa','#bfebfa','#bce7fa','#b9e3fa','#b6dff9','#b3dbf9','#b0d6f9','#add1f9','#aacbf9','#a7c6f9','#a5c0f9','#a2baf9','#9fb4f8','#9cadf8','#99a6f8','#969ff8','#9398f8','#9190f8','#938df8','#958bf7','#9888f7','#9b85f7','#9e82f7','#a17ff7','#a57cf7','#a979f7','#ad77f6','#b174f6','#b671f6','#bb6ef6','#c06bf6','#c668f6','#cb65f5','#d163f5','#d860f5','#de5df5','#e55af5','#ec57f5','#f355f5','#f452ef','#f44fe7','#f44cde','#f449d6','#f447cd','#f444c4','#f441bb','#f33eb1','#f33ba8','#f3399e','#f33693','#f33389','#f3307e','#f32e73','#f22b68','#f2285c','#f22551','#f22245','#f22039','#f21d2c','#f21a1f','#f11d17']
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
    times = ["1a", "2a", "3a", "4a", "5a", "6a", "7a", "8a", "9a", "10a", "11a", "12a", "1p", "2p", "3p", "4p", "5p", "6p", "7p", "8p", "9p", "10p", "11p", "12p"];
    // datasets = ["data/weekheatmap-northrend-solo.csv", "data/weekheatmap-northrend-random4v4.csv", "data/weekheatmap-azeroth-solo.csv", "data/weekheatmap-azeroth-random4v4.csv"];
    gateways = ["northrend", "azeroth", "lordaeron", "kalimdor"]
    gametypes = ["solo", "random2v2", "random3v3", "random4v4", "arranged2v2", "arranged3v3", "arranged4v4", "tournament", "ffa"]
    var datasets = []

    gateways.forEach(function(gateway){
      gametypes.forEach(function(gametype){
        datasets.push("data/weekheatmap-" + gateway + "-" + gametype + ".csv")
      })
    })

    console.log(datasets)


  var svg = d3.select("#chart").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  var hourLabels = svg.selectAll(".hourLabel")
    .data(times)
    .enter().append("text")
    .text(function (d) { return d; })
    .attr("x", 0)
    .attr("y", function (d, i) { return i * gridSize; })
    .style("text-anchor", "end")
    .attr("transform", "translate(-6," + gridSize / 1.5 + ")")
    .attr("class", function (d, i) { return ((i >= 0) ? "hourLabel mono axis axis-workweek" : "hourLabel mono axis"); });

  var dayLabels = svg.selectAll(".dayLabel")
    .data(days)
    .enter().append("text")
    .text(function (d) { return d; })
    .attr("x", function (d, i) { return i * gridSize * 4 + gridSize * 1.5; })
    .attr("y", 0)
    .style("text-anchor", "middle")
    .attr("transform", "translate(" + gridSize / 2 + ", -6)")
    .attr("class", function (d, i) { return ((i >= 7 && i <= 16) ? "dayLabel mono axis axis-worktime" : "dayLabel mono axis"); });

  var heatmapChart = function (csvFile) {
    d3.csv(csvFile,
      function (d) {
        return {
          weekday: +d.weekday + 1,
          hour: +d.hour + 1,
          games: +d.games
        };
      },
      function (error, data) {
        var colorScale = d3.scale.quantile()
          .domain([d3.max(data, function (d) { return d.games; }) / 5, buckets / 5, d3.max(data, function (d) { return d.games; })])
          .range(colors);

        var cards = svg.selectAll(".hour")
          .data(data, function (d) { return d.weekday + ':' + d.hour; });

        cards.append("title");

        cards.enter().append("rect")
          .attr("y", function (d) { return (d.hour - 1) * gridSize; })
          .attr("x", function (d) { return (d.weekday - 1) * gridSize * 4; })
          .attr("rx", 4)
          .attr("ry", 4)
          .attr("class", "hour bordered")
          .attr("width", gridSize * 4)
          .attr("height", gridSize)
          .style("fill", colors[0]);

        cards.transition().duration(1000)
          .style("fill", function (d) { return colorScale(d.games); });

        cards.select("title").text(function (d) { return d.games; });

        cards.exit().remove();

        var legend = svg.selectAll(".legend")
          .data([0].concat(colorScale.quantiles()), function (d) { return d; });

        legend.enter().append("g")
          .attr("class", "legend");

        legend.append("rect")
          .attr("x", function (d, i) { return (width / colors.length / 1.775) * i; })
          .attr("y", height)
          .attr("width", legendElementWidth)
          .attr("height", gridSize / 2)
          .style("fill", function (d, i) { return colors[i]; });

        // legend.append("text")
        //   .attr("class", "mono")
        //   .text(function (d) { return "≥ " + Math.round(d); })
        //   .attr("x", function (d, i) { return (width / colors.length / 1.77) * i; })
        //   .attr("y", height + gridSize)

        legend.exit().remove();

      });
  };

  heatmapChart(datasets[0]);

  var datasetpicker = d3.select("#dataset-picker").selectAll(".dataset-button")
    .data(datasets);

  datasetpicker.enter()
    .append("input")
    .attr("value", function (d) { return d })
    .attr("type", "button")
    .attr("class", "dataset-button")
    .on("click", function (d) {
      heatmapChart(d);
    });
});