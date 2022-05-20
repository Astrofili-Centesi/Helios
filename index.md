---
layout: default
title: Astrofili Centesi - Sistema Helios
---


# Astrofili Centesi - Sistema Helios

## Dati delle ultime 24h di registrazione


<div id="plotlyDiv"></div>



## Il sistema Helios VLF solar telescope

Helios VLF è uno strumento di tipo ROEON destinato a raccogliere informazioni sui brillamenti solari, sulle tempeste geomagnetiche, sulle scariche atmosferiche se su tanti altri eventi di origine naturale.

Le sue lunghe braccia gli conferiscono un'alta sensibilità che consente di raccogliere dati accurati.

Il sistema si compone di un dipolo a correnti di terra con ampia area di cattura, di un circuito di trattamento del segnale, di un acquisitore, di un sistema di elaborazione matematica del segnale e infine di un logger in grado di archiviare l'intera quantità di dati
elaborati, che sono poi [resi disponibili su internet](https://github.com/Astrofili-Centesi/Helios).

L'antenna di 25m è totalmente interrata, offre una buona sensibilità a fronte di un eccezionale rapporto segnale/rumore ed è completamente invisibile.

L'intero sistema è stato progettato e costruito dagli [Astrofili Centesi](https://www.astrofilicentesi.it/).




<script src="https://code.jquery.com/jquery-3.6.0.min.js" integrity="sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js/dist/chart.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js"></script>

<script src='https://cdn.plot.ly/plotly-2.11.1.min.js'></script>

<script>

function renderChart(labels,ch1,ch2,ch3) {
    var ctx = document.getElementById("myChart").getContext('2d');

    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [ch1,ch2,ch3]
        },
        options: {
elements: {
point: {
radius: 0
}
},
plugins: {
            title: {
                display: true,
                text: "Acquisizione sistema Helios"
            }
            },
            scales: {
            x: {
                type: 'time',
                ticks: {
source:'data'},
time: { unit: 'second',
displayFormats: {
second: 'yyyy-MM-dd hh:mm:ss'}
            }
        }
        }
    }});



}

var layout = {
xaxis: {
title: 'timestamp'
       },
yaxis: {
title: "dB"
       }
};

function plotPlotly(ch1data,ch2data,ch3data) {
var plotlydata=[ch1data,ch2data,ch3data];
Plotly.newPlot('plotlyDiv',plotlydata, layout);
}

var labels=[];
var ch1data={type:'scatter', mode: 'lines', name:'HWU', x:[],y:[]};
var ch2data={type:'scatter', mode: 'lines', name:'ICV', x:[],y:[]};
var ch3data={type:'scatter', mode: 'lines', name:'noise', x:[],y:[]};

$.getJSON( "{{site.baseurl}}/data/db_latest.json", function( inputdata ) {

        var ch1={
label: 'ch1',
backgroundColor: 'rgb(255, 99, 132)',
           borderColor: 'rgb(255, 99, 132)',
           showLine: true,
data: []
};

  $.each(inputdata['ch1'], function( key, val ) {
      labels.push(parseInt(key));
          ch1['data'].push({'x':parseInt(key),'y':val});
          ch1data['x'].push(new Date(parseInt(key)).toISOString());
          ch1data['y'].push(val);
  });

        var ch2={
label: 'ch2',
backgroundColor: 'rgb(218, 247, 166)',
           borderColor: 'rgb(218, 247, 166)',
           showLine: true,
data: []
};

  $.each(inputdata['ch2'], function( key, val ) {
          ch2['data'].push({'x':parseInt(key),'y':val});
          ch2data['x'].push(new Date(parseInt(key)).toISOString());
          ch2data['y'].push(val);
  });


        var ch3={
label: 'ch3',
backgroundColor: 'rgb(144, 12, 63)',
           borderColor: 'rgb(144, 12, 63)',
           showLine: true,
data: []
};

  $.each(inputdata['ch3'], function( key, val ) {
          ch3['data'].push({'x':parseInt(key),'y':val});
          ch3data['x'].push(new Date(parseInt(key)).toISOString());
          ch3data['y'].push(val);
  });

//renderChart(labels,ch1,ch2,ch3);
plotPlotly(ch1data,ch2data,ch3data);

//datasets.push(ch2);
//datasets.push(ch3);
 
});



</script>



