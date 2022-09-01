---
layout: default
title: Astrofili Centesi - Sistema Helios
---

# Astrofili Centesi - Sistema Helios

## Dati delle ultime 24h di registrazione

<div id="plotlyDiv"></div>

FTA e HWU sono le sigle di due trasmettitori NATO:

* FTA è un trasmettitore in Francia nei pressi di Seine-et-Marne
* HWU è un trasmettitore in Francia nei pressi di Rosnay
* DCF77 è un trasmettitore in Germania per la diffusione del segnale orario

## Dati dell'ultimo mese di registrazione

(utilizzare i bottoni o lo slider per navigare)

<div id="plotlyDiv4"></div>

<!-- IN MANUTENZIONE
## Dati medi degli ultimi 5 giorni di registrazione

<div id="plotlyDiv3"></div>
-->

## Spettrogramma del segnale

(ultimi 10 secondi)

<img src="https://raw.githubusercontent.com/Astrofili-Centesi/Helios/main/spectrogram.png" class="center img-fluid"> 

## Il sistema Helios VLF solar telescope

Helios VLF è uno strumento di tipo ROEON (Rivelatore Onde Elettromagnetiche di Origine Naturale) destinato a raccogliere informazioni sui brillamenti solari, sulle tempeste geomagnetiche, sulle scariche atmosferiche se su tanti altri eventi di origine naturale.

Le sue lunghe "braccia" gli conferiscono un'alta sensibilità che consente di raccogliere dati accurati.

Il sistema si compone di un dipolo a correnti di terra con ampia area di cattura, di un circuito di trattamento del segnale, di un acquisitore, di un sistema di elaborazione matematica del segnale e infine di un logger in grado di archiviare l'intera quantità di dati
elaborati, che sono poi [resi disponibili su internet](https://github.com/Astrofili-Centesi/Helios).

L'antenna, di 25m, è totalmente interrata, offre una buona sensibilità a fronte di un eccezionale rapporto segnale/rumore ed è completamente invisibile.

L'intero sistema è stato progettato e costruito dagli [Astrofili Centesi](https://www.astrofilicentesi.it/).


<script src="https://code.jquery.com/jquery-3.6.0.min.js" integrity="sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js/dist/chart.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js"></script>

<script src='https://cdn.plot.ly/plotly-2.11.1.min.js'></script>

<script>


const layout_base = {
height: 800,
xaxis: {
title: 'timestamp'
       },
yaxis: {
title: "dBFS",
//range: [-100,-20]
       }
};

function plotPlotly(divname,ch1data,ch2data,ch3data,layout) {
var plotlydata=[ch1data,ch2data,ch3data];
Plotly.newPlot(divname,plotlydata, layout);
}


$.getJSON( "{{site.baseurl}}/data/db_latest.json", function( inputdata ) {
var labels=[];
var ch1data={type:'scatter', mode: 'lines', name:'FTA', x:[],y:[]};
var ch2data={type:'scatter', mode: 'lines', name:'HWU', x:[],y:[]};
var ch3data={type:'scatter', mode: 'lines', name:'DCF77', x:[],y:[]};

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

plotPlotly('plotlyDiv',ch1data,ch2data,ch3data,layout_base);

});


//$.getJSON( "{{site.baseurl}}/data/db_latest_day.json", function( inputdata ) {
//var labels=[];
//var ch1data={type:'scatter', mode: 'lines', name:'HWU', x:[],y:[]};
//var ch2data={type:'scatter', mode: 'lines', name:'ICV', x:[],y:[]};
//var ch3data={type:'scatter', mode: 'lines', name:'noise', x:[],y:[]};
//
//        var ch1={
//label: 'ch1',
//backgroundColor: 'rgb(255, 99, 132)',
//           borderColor: 'rgb(255, 99, 132)',
//           showLine: true,
//data: []
//};
//
//  $.each(inputdata['ch1'], function( key, val ) {
//      labels.push(parseInt(key));
//          ch1['data'].push({'x':parseInt(key),'y':val});
//          ch1data['x'].push(new Date(parseInt(key)).toISOString());
//          ch1data['y'].push(val);
//  });
//
//        var ch2={
//label: 'ch2',
//backgroundColor: 'rgb(218, 247, 166)',
//           borderColor: 'rgb(218, 247, 166)',
//           showLine: true,
//data: []
//};
//
//  $.each(inputdata['ch2'], function( key, val ) {
//          ch2['data'].push({'x':parseInt(key),'y':val});
//          ch2data['x'].push(new Date(parseInt(key)).toISOString());
//          ch2data['y'].push(val);
//  });
//
//
//        var ch3={
//label: 'ch3',
//backgroundColor: 'rgb(144, 12, 63)',
//           borderColor: 'rgb(144, 12, 63)',
//           showLine: true,
//data: []
//};
//
//  $.each(inputdata['ch3'], function( key, val ) {
//          ch3['data'].push({'x':parseInt(key),'y':val});
//          ch3data['x'].push(new Date(parseInt(key)).toISOString());
//          ch3data['y'].push(val);
//  });
//
//plotPlotly('plotlyDiv2',ch1data,ch2data,ch3data,layout_base);
//
//});

function addZero(i) {
  if (i < 10) {i = "0" + i}
  return i;
}

function stripDate(timestamp)
{
    var d = new Date(parseInt(timestamp));
    return addZero(d.getHours()) + ":" + addZero(d.getMinutes()) + ":" + addZero(d.getSeconds());
}


$.when(
    $.getJSON( "{{site.baseurl}}/data/db_mean_5days.json" ),
    $.getJSON( "{{site.baseurl}}/data/db_latest_day.json" )
).done(function(mean5days, latest_day) {

var labels=[];
var ch1data={type:'scatter', mode: 'lines', name:'HWU_mean5d', x:[],y:[]};
var ch2data={type:'scatter', mode: 'lines', name:'ICV_mean5d', x:[],y:[]};
var ch3data={type:'scatter', mode: 'lines', name:'noise_mean5d', x:[],y:[]};
var ch1_1data={type:'scatter', mode: 'lines', name:'noise_1d', x:[],y:[]};
var ch2_1data={type:'scatter', mode: 'lines', name:'HWU_1d', x:[],y:[]};
var ch3_1data={type:'scatter', mode: 'lines', name:'ICV_1d', x:[],y:[]};


  $.each(mean5days[0]['ch1'], function( key, val ) {
      labels.push(parseInt(key));
          ch1data['x'].push(stripDate(key));
          ch1data['y'].push(val);
  });

  $.each(mean5days[0]['ch2'], function( key, val ) {
          ch2data['x'].push(stripDate(key));
          ch2data['y'].push(val);
  });

  $.each(mean5days[0]['ch3'], function( key, val ) {
          ch3data['x'].push(stripDate(key));
          ch3data['y'].push(val);
  });

  $.each(latest_day[0]['ch1'], function( key, val ) {
      labels.push(parseInt(key));
          ch1_1data['x'].push(stripDate(key));
          ch1_1data['y'].push(val);
  });

  $.each(latest_day[0]['ch2'], function( key, val ) {
          ch2_1data['x'].push(stripDate(key));
          ch2_1data['y'].push(val);
  });

  $.each(latest_day[0]['ch3'], function( key, val ) {
          ch3_1data['x'].push(stripDate(key));
          ch3_1data['y'].push(val);
  });

var plotlydata=[ch1data,ch2data,ch3data,ch1_1data,ch2_1data,ch3_1data];
//var plotlydata=[ch1_1data,ch2_1data,ch3_1data];
//var plotlydata=[ch1data,ch2data,ch3data];
const layout = {
height: 800,
        xaxis: {
title: 'timestamp',
        },
yaxis: {
title: "dBFS",
//range: [-100,-20]
       }
};
Plotly.newPlot('plotlyDiv3',plotlydata,layout);
//plotPlotly('plotlyDiv3',ch1data,ch2data,ch3data,ch1_1data,ch2_1data,ch3_1data,layout_base);

});

$.getJSON( "{{site.baseurl}}/data/db_latest_month.json", function( inputdata ) {
var labels=[];
var ch1data={type:'scatter', mode: 'lines', name:'FTA', x:[],y:[]};
var ch2data={type:'scatter', mode: 'lines', name:'HWU', x:[],y:[]};
var ch3data={type:'scatter', mode: 'lines', name:'DCF77', x:[],y:[]};

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

var selectorOptions = {

    buttons: [{

        step: 'day',

        stepmode: 'backward',

        count: 1,

        label: '1d'

    }, {

        step: 'day',

        stepmode: 'backward',

        count: 7,

        label: '1w'

    }, {

        step: 'all',

    }],

};

const layout_slider = {
height: 800,
        xaxis: {
title: 'timestamp',
       rangeselector: selectorOptions,

       rangeslider: { range: 864000 }

        },
yaxis: {
fixedrange: false,
title: "dBFS",
//range: [-100,-20]
       }
};

plotPlotly('plotlyDiv4',ch1data,ch2data,ch3data,layout_slider);

});

</script>



