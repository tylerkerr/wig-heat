$(function () {
  var margin = { top: 50, right: 0, bottom: 100, left: 30 },
    width = 1230 - margin.left - margin.right,
    height = 800 - margin.top - margin.bottom,
    gridSize = Math.floor(height / 24),
    legendElementWidth = gridSize * 3.11,
    buckets = 9,
    // colors = ["#ffffd9","#edf8b1","#c7e9b4","#7fcdbb","#41b6c4","#1d91c0","#225ea8","#253494","#081d58"], // alternatively colorbrewer.YlGnBu[9]
    colors = ["#f7feff", "#e6fffd", "#dcffd5", "#caff76", "#fff600", "#ffd200", "#ffa200", "#ff7200", "#ff0000"], // alternatively colorbrewer.YlGnBu[9]
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
    times = ["1a", "2a", "3a", "4a", "5a", "6a", "7a", "8a", "9a", "10a", "11a", "12a", "1p", "2p", "3p", "4p", "5p", "6p", "7p", "8p", "9p", "10p", "11p", "12p"];
  datasets = ["weekheatmap-northrend-solo.csv", "weekheatmap-northrend-arranged3v3.csv", "weekheatmap-northrend-arranged4v4.csv", "weekheatmap-northrend-random4v4.csv"];

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
          .domain([d3.max(data, function (d) { return d.games; }) / 5, buckets - 5, d3.max(data, function (d) { return d.games; })])
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
          .attr("x", function (d, i) { return legendElementWidth * i; })
          .attr("y", height)
          .attr("width", legendElementWidth)
          .attr("height", gridSize / 2)
          .style("fill", function (d, i) { return colors[i]; });

        legend.append("text")
          .attr("class", "mono")
          .text(function (d) { return "≥ " + Math.round(d); })
          .attr("x", function (d, i) { return legendElementWidth * i; })
          .attr("y", height + gridSize);

        legend.exit().remove();

      });
  };

  heatmapChart(datasets[0]);

  var datasetpicker = d3.select("#dataset-picker").selectAll(".dataset-button")
    .data(datasets);

  datasetpicker.enter()
    .append("input")
    .attr("value", function (d) { return "Dataset " + d })
    .attr("type", "button")
    .attr("class", "dataset-button")
    .on("click", function (d) {
      heatmapChart(d);
    });
});