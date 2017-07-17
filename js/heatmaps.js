$(function () {
  var margin = { top: 40, right: 0, bottom: 40, left: 30 },
    width = 1000 - margin.left - margin.right,
    height = 800 - margin.top - margin.bottom,
    gridSize = Math.floor(height / 24),
    legendElementWidth = gridSize * 3.11,
    buckets = 5
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
    times = ["1a", "2a", "3a", "4a", "5a", "6a", "7a", "8a", "9a", "10a", "11a", "12a", "1p", "2p", "3p", "4p", "5p", "6p", "7p", "8p", "9p", "10p", "11p", "12p"];
    gateways = ["Northrend", "Azeroth", "Lordaeron", "Kalimdor"]
    gametypes = ["Solo", "Random 2v2", "Random 3v3", "Random 4v4", "Arranged 2v2", "Arranged 3v3", "Arranged 4v4", "Tournament", "FFA"]
    var datasets = []
    gateways.forEach(function(gateway){
      gametypes.forEach(function(gametype){
        datasets.push(gateway + " - " + gametype)
      })
    })


  var makefilename = function (d){
    return "/data/weekheatmap-" +  d.toLowerCase().replace(/\s/g, '') + ".csv"
  }

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
        var minval = 0
        var maxval = d3.max(data, function (d) { return d.games; })

        if (maxval == minval) {
          colors = ["#ffffff"]
        } else {
          colors = ["#ffffff", "#fefefe", "#fefdfd", "#fefcfc", "#fefcfb", "#fefbfa", "#fefbf9", "#fefaf9", "#fefaf8", "#fefaf7", "#fefaf6", "#fefaf5", "#fefaf4", "#fefaf3", "#fefaf2", "#fdfbf1", "#fdfbf0", "#fdfcef", "#fdfdee", "#fdfded", "#fcfdec", "#fbfdeb", "#fafdeb", "#f9fdea", "#f8fde9", "#f6fde8", "#f5fde7", "#f4fde6", "#f2fde6", "#f0fde5", "#effce4", "#edfce3", "#ebfce2", "#e9fce1", "#e8fce1", "#e5fce0", "#e3fcdf", "#e1fcde", "#dffcdd", "#ddfcdc", "#dcfcdd", "#dbfcde", "#dafcdf", "#d9fce0", "#d8fce1", "#d8fce2", "#d7fbe3", "#d6fbe4", "#d5fbe6", "#d4fbe7", "#d3fbe8", "#d3fbea", "#d2fbec", "#d1fbed", "#d0fbef", "#cffbf1", "#cffbf3", "#cefbf5", "#cdfbf7", "#ccfbf9", "#cbfafb", '#caf7fa','#c8f5fa','#c5f2fa','#c2effa','#bfebfa','#bce7fa','#b9e3fa','#b6dff9','#b3dbf9','#b0d6f9','#add1f9','#aacbf9','#a7c6f9','#a5c0f9','#a2baf9','#9fb4f8','#9cadf8','#99a6f8','#969ff8','#9398f8','#9190f8','#938df8','#958bf7','#9888f7','#9b85f7','#9e82f7','#a17ff7','#a57cf7','#a979f7','#ad77f6','#b174f6','#b671f6','#bb6ef6','#c06bf6','#c668f6','#cb65f5','#d163f5','#d860f5','#de5df5','#e55af5','#ec57f5','#f355f5','#f452ef','#f44fe7','#f44cde','#f449d6','#f447cd','#f444c4','#f441bb','#f33eb1','#f33ba8','#f3399e','#f33693','#f33389','#f3307e','#f32e73','#f22b68','#f2285c','#f22551','#f22245','#f22039','#f21d2c','#f21a1f','#f11d17']
        }

        var colorScale = d3.scale.quantile()
          .domain([d3.max(data, function (d) { return d.games; }) / 5, buckets, d3.max(data, function (d) { return d.games; })])
          .range(colors);

        var cards = svg.selectAll(".hour")
          .data(data, function (d) { return d.weekday + ':' + d.hour; });


        cards.enter().append("rect")
          .attr("y", function (d) { return (d.hour - 1) * gridSize; })
          .attr("x", function (d) { return (d.weekday - 1) * gridSize * 4; })
          // .attr("rx", 4)
          // .attr("ry", 4)
          .attr("class", "hour bordered")
          .attr("width", gridSize * 4)
          .attr("height", gridSize)
          .style("fill", colors[0])
          .on("mouseover",function(d){
            d3.select('[data-id="' + d.weekday + ':' + d.hour +'"]')
            .attr("opacity", "1")
          })
          .on("mouseout",function(d){
            d3.select('[data-id="' + d.weekday + ':' + d.hour +'"]' )
            .attr("opacity", "0")
          });


        var txt = svg.selectAll("g")
          .data(data)
          .enter().append("g")  

        txt.append("text")
              .attr("y", function (d) { return (d.hour - 1) * gridSize + gridSize * 0.72; })
              .attr("x", function (d) { return (d.weekday - 1) * gridSize * 4 + gridSize * 1.4; })
              .attr("data-id", function (d) { return d.weekday + ':' + d.hour; })
              .attr("class", "cellcount")
              .attr("opacity", "0")
              .attr("color", "#ccc")
              .text(function(d) { return d.games; })
              .on("mouseover",function(d){
                d3.select('[data-id="' + d.weekday + ':' + d.hour +'"]')
                .attr("opacity", "1")
              })
              .on("mouseout",function(d){
                d3.select('[data-id="' + d.weekday + ':' + d.hour +'"]' )
                .attr("opacity", "0")
              });

        cards.transition().duration(500)
          .style("fill", function (d) { return colorScale(d.games); });


        cards.exit().remove();


        var legend = svg.selectAll(".legend")
          .data([0].concat(colorScale.quantiles()), function (d) { return d; });

        legend.enter().append("g")
          .attr("class", "legend");

        legend.append("rect")
          .attr("x", function (d, i) { return (width*0.7755 / colors.length) * i; })
          .attr("y", height + .5)
          .attr("width", legendElementWidth)
          .attr("height", gridSize / 2)
          .style("fill", function (d, i) { return colors[i]; });

        legend.append("text")
          .attr("class", "mono")
          .text(function (d,i) { 
            if ((i+1) == colors.length) {
              return maxval
            } else if ((i !== 0) && ((i+1)%25)) {
              return null
            } else {
              return Math.round(d);
            }
          })
          .attr("x", function (d, i) { return (width*0.85 / colors.length) * i; })
          .attr("y", height + gridSize)

        legend.append("text")
          .attr("class", "mono")
          .text(minval)
          .attr("x", width)
          .attr("y", height + gridSize)

        legend.exit().remove();
        
      });
  };

  heatmapChart(makefilename(datasets[0]));

  $(document).on("change","input[type=radio]",function(){
      var gateway=$('[name="gateway"]:checked').val();
      var gametype= $('[name="gametype"]:checked').length>0? $('[name="gametype"]:checked').val():"";
      heatmapChart(makefilename(gateway + "-" + gametype))
  });


});


