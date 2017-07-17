var gateways = ["allrealms", "azeroth", "northrend", "lordaeron", "kalimdor"]

if(window.location.hash) {
  var frag = window.location.hash.replace("#", "")
  if (gateways.indexOf(frag) >= 0) {
    var selectedGateway = frag
  }
  else {
    var selectedGateway = gateways[0]
    window.location.hash = '#' + gateways[0];
  }
} else {
  var selectedGateway = gateways[0]
}

var processedGatewayData = {}
var loadedDataCount = 0;
var chart, chartData; 

document.getElementById("tab-" + selectedGateway).className += " active"

gateways.forEach(function(gateway){
  var tab = document.querySelector('#tab-' + gateway)
  var chart = document.querySelector('#chart-' + gateway)

  // bind click event to tab
  tab.onclick = function(){
      update(gateway)
  }

  // process csv data 
  d3.csv("/data/gamesbytype-" + gateway + ".csv",function(err,data){
      var dataToPlot = Object.keys(data[0]).filter(function(k){return k!="date"})
        .map(function(k){
          return {"key":k,"values":data.map(function(d){  
           return {
             "x":d3.time.format("%Y-%m-%d").parse(d.date),
             "y":+d[k]
           }
          })}
        })

      processedGatewayData[gateway] = dataToPlot
      loadedDataCount ++;
    })
})

function update(gateway) {
    document.getElementById("tab-" + selectedGateway).classList.remove("active")
    selectedGateway = gateway
    document.getElementById("tab-" + selectedGateway).className += " active"
    var data = processedGatewayData[gateway]
    chartData.datum(data).transition().duration(500).call(chart);
    nv.utils.windowResize(chart.update);
    d3.select('#chart' + selectedGateway + ' svg')
      .append("text")
      .attr("x", 200)             
      .attr("y", 100)
      .attr("text-anchor", "middle")  
      .text("Sample Charts");
};

var tryCreateChart = setInterval(function(){

if (loadedDataCount == gateways.length) {
  nv.addGraph(function() {
    chart = nv.models.lineWithFocusChart();

    chart.xAxis
        .tickFormat(function(d) { return d3.time.format('%Y-%-m-%-d')(new Date(d)) })
    chart.x2Axis
        .tickFormat(function(d) { return ''})

    chart.yAxis
        .tickFormat();
    chart.y2Axis
      .tickFormat(function(d) { return ''})


    chart.color(function(d) {
      if (d.key == 'Northrend') return '#75a7e8';
      if (d.key == 'Azeroth') return '#d62728';
      if (d.key == 'Lordaeron') return '#255ddc';
      if (d.key == 'Kalimdor') return '#6b23ad';
      if (d.key == 'Solo') return '#1f77b4';
      if (d.key == 'FFA') return '#ffa10d';
      if (d.key == 'Tournament') return '#bbbbbb';
      if (d.key == 'Random 2v2') return '#e9d9ff';
      if (d.key == 'Random 3v3') return '#ff8c9c';
      if (d.key == 'Random 4v4') return '#ff4eba';
      if (d.key == 'Arranged 2v2') return '#aec7e8';
      if (d.key == 'Arranged 3v3') return '#50e8e6';
      if (d.key == 'Arranged 4v4') return '#15e82e';
    })

    chartData = d3.select('#chart svg')
        .datum(processedGatewayData[selectedGateway])

    chartData.transition().duration(500)
        .call(chart);

    nv.utils.windowResize(chart.update);

    return chart;
  }); 
  clearInterval(tryCreateChart);
}
},15);
