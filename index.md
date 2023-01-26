---
layout: default
title: Astrofili Centesi - Sistema Helios
---

# Astrofili Centesi - Sistema Helios

## Dati delle ultime 24h di registrazione

<div id="plotlyDiv"></div>

HWU, FTA, ICV, ecc... sulla destra del grafico sono
le sigle dei trasmettitori VLF utilizzati.

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

Il funzionamento di Helios è stato documentato in questo articolo [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7097629.svg)](https://doi.org/10.5281/zenodo.7097629).



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

function plotPlotly(divname,channels,layout) {
var plotlydata=channels;
Plotly.newPlot(divname,plotlydata, layout);
}


function plotJSON(filename,divname,layout) {
    $.getJSON( filename, function( inputdata ) {
            var labels=[];
            var channels=[];

            $.each(inputdata, function(channel_name, channel_data) {
                    var chdata={type:'scatter', mode: 'lines', name:channel_name, x:[],y:[]};
                    var ch={
label: channel_name,
showLine: true,
data: []
};

$.each(channel_data, function( key, val ) {
    labels.push(parseInt(key));
    ch['data'].push({'x':parseInt(key),'y':val});
    chdata['x'].push(new Date(parseInt(key)).toISOString());
    chdata['y'].push(val);
    });

channels.push(chdata);
});

plotPlotly(divname,channels,layout);
});
}

plotJSON("{{site.baseurl}}/data/db_latest.json",'plotlyDiv',layout_base);


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

plotJSON("{{site.baseurl}}/data/db_latest_month.json", 'plotlyDiv4', layout_slider);

function addZero(i) {
  if (i < 10) {i = "0" + i}
  return i;
}

function stripDate(timestamp)
{
    var d = new Date(parseInt(timestamp));
    return addZero(d.getHours()) + ":" + addZero(d.getMinutes()) + ":" + addZero(d.getSeconds());
}


//$.when(
//    $.getJSON( "{{site.baseurl}}/data/db_mean_5days.json" ),
//    $.getJSON( "{{site.baseurl}}/data/db_latest_day.json" )
//).done(function(mean5days, latest_day) {
//
//var labels=[];
//var ch1data={type:'scatter', mode: 'lines', name:'HWU_mean5d', x:[],y:[]};
//var ch2data={type:'scatter', mode: 'lines', name:'ICV_mean5d', x:[],y:[]};
//var ch3data={type:'scatter', mode: 'lines', name:'noise_mean5d', x:[],y:[]};
//var ch1_1data={type:'scatter', mode: 'lines', name:'noise_1d', x:[],y:[]};
//var ch2_1data={type:'scatter', mode: 'lines', name:'HWU_1d', x:[],y:[]};
//var ch3_1data={type:'scatter', mode: 'lines', name:'ICV_1d', x:[],y:[]};
//
//
//  $.each(mean5days[0]['ch1'], function( key, val ) {
//      labels.push(parseInt(key));
//          ch1data['x'].push(stripDate(key));
//          ch1data['y'].push(val);
//  });
//
//  $.each(mean5days[0]['ch2'], function( key, val ) {
//          ch2data['x'].push(stripDate(key));
//          ch2data['y'].push(val);
//  });
//
//  $.each(mean5days[0]['ch3'], function( key, val ) {
//          ch3data['x'].push(stripDate(key));
//          ch3data['y'].push(val);
//  });
//
//  $.each(latest_day[0]['ch1'], function( key, val ) {
//      labels.push(parseInt(key));
//          ch1_1data['x'].push(stripDate(key));
//          ch1_1data['y'].push(val);
//  });
//
//  $.each(latest_day[0]['ch2'], function( key, val ) {
//          ch2_1data['x'].push(stripDate(key));
//          ch2_1data['y'].push(val);
//  });
//
//  $.each(latest_day[0]['ch3'], function( key, val ) {
//          ch3_1data['x'].push(stripDate(key));
//          ch3_1data['y'].push(val);
//  });
//
//var plotlydata=[ch1data,ch2data,ch3data,ch1_1data,ch2_1data,ch3_1data];
////var plotlydata=[ch1_1data,ch2_1data,ch3_1data];
////var plotlydata=[ch1data,ch2data,ch3data];
//const layout = {
//height: 800,
//        xaxis: {
//title: 'timestamp',
//        },
//yaxis: {
//title: "dBFS",
////range: [-100,-20]
//       }
//};
//Plotly.newPlot('plotlyDiv3',plotlydata,layout);
////plotPlotly('plotlyDiv3',ch1data,ch2data,ch3data,ch1_1data,ch2_1data,ch3_1data,layout_base);
//
//});

</script>



