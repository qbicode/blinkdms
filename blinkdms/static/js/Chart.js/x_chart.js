/**
 * manage Chart.js for the application ... 
 * @author  Steffen Kube (steffen@blink-dx.com)
 */
 
/**
    show chart
    @param id: ID of element
    @param chart_type: 'pie', 'bar', 'line'
      'line': time graph
    @param data:  {
	datasets: [{
	    data: [] 
	    }
    @param config
       'label_names' : 0,1
       'label_values': 0,1
    
 */
 
var COLORS = [
	'#4dc9f6',
	'#f67019',
	'#00a950',
	'#f53794',
	'#537bc4',
	'#acc236',
	'#166a8f',
	'#58595b',
	'#8549ba'
    ];
 

function x_chart_color(index) {
    return COLORS[index % COLORS.length];
}

function x_fill_dataset_colors(  datasets  ) {
    i=0
    for (row of datasets ) {
	row['backgroundColor'] = x_chart_color(i);
	datasets[i] = row
	i=i+1;
    }
}
	    
/* 
{# 
:param data_conf: 
  'data': 
  'options':
    'title' : title of dia
    'yAxes'['label'] : label text
:param config:
    'label_names' : 0,1
    'label_values': 0,1
    'data.backcolor' : 0,1 (for chart_type=='line')
#}
*/
function x_show_chart( id, chart_type, data_conf, config={} ) {

    var chartColors = {
	red: 'rgb(255, 99, 132)',
	orange: 'rgb(255, 159, 64)',
	yellow: 'rgb(255, 205, 86)',
	green: 'rgb(75, 192, 192)',
	blue: 'rgb(54, 162, 235)',
	purple: 'rgb(153, 102, 255)',
	grey: 'rgb(201, 203, 207)'
    };

    var options = {};
    var ctx = document.getElementById(id);
    
    options['scales'] = {}
    
    if (chart_type=='pie') {
    
        var options = {
	    legend: {
		display: false
	    },
	    responsive: true,
	    
	};
	
	if (config['label_names']>0) {
	    options['plugins'] = {
	        labels: [
		    {
		      render: 'label',
		      position: 'outside'
		    },
		    
	        ]
	    };
	}
	if (config['label_values']>0) {
	    options['plugins']['labels'].push( {
		      render: 'value'
		} );
	}
	
	data_conf['data']['datasets'][0]['backgroundColor'] = [
	    chartColors.red,
	    chartColors.orange,
	    chartColors.yellow,
	    chartColors.green,
	    chartColors.blue,
	];
    }
    
    if (chart_type=='bar') {
        var options = {
	    maintainAspectRatio: false,
	    scales: {
		xAxes: [{
			stacked: true,
		}],
		yAxes: [{
			stacked: true
		}]
	    },
	    tooltips: {
		mode: 'index',
		intersect: false
	    },
	    responsive: true,
	    plugins: {
		'labels': false /* deactivate here, otherwise shows PERECNT ! */
		},
	};
	
	x_fill_dataset_colors( data_conf['data']['datasets'] );
    }
    
    if (chart_type=='line') {
    
	if ( config['data.backcolor'] ) {
	    var i=0;
	    for (row of data_conf['data']['datasets'] ) {
		row['backgroundColor'] = x_chart_color(i);
		row['borderColor']     = i;
		row['hidden']          = false;
		data_conf['data']['datasets'][i] = row
		i=i+1;
	    }
	}
        
        var options = {
	    maintainAspectRatio: false,
	    spanGaps: false,
	    elements: {
		    line: {
			tension: 0.000001
		    }
	    },
	    scales: {
		xAxes: [{
			    stacked: true,
		    }],
		yAxes: [
		{
		    stacked: true
		}]
	    },
	    plugins: {
		    filler: {
			propagate: false
		    },
		    
	    }
	};

	
    }
    
    if (data_conf['options']['title']!='') {
	options['title'] = {};
	options['title']['display'] = true;
	options['title']['text'] = data_conf['options']['title'];
    }
    
    if ( data_conf['options']['yAxes'] ) {
        if ( data_conf['options']['yAxes']['label']) {
	
	    options['scales']['yAxes']['display'] = true;
	    options['scales']['yAxes'][0]['scaleLabel'] = {
		display: true,
		labelString:  data_conf['options']['yAxes']['label']
	    };
	}
    }


    var myChart = new Chart(
        ctx, 
        {
	    type: chart_type,
	    data: data_conf['data'],
	    options: options
        } 
    );
    
   
   

}


