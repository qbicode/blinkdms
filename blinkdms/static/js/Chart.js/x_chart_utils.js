/**
 * utilities ...
 * manage Chart.js for the application ... 
 * @author  Steffen Kube (steffen@blink-dx.com)
 */

(function(global) {

    var COLORS = [
	'#4dc9f6',
	'#f67019',
	'#f53794',
	'#537bc4',
	'#acc236',
	'#166a8f',
	'#00a950',
	'#58595b',
	'#8549ba'
    ];
    
    var Chart = global.Chart || (global.Chart = {});

    Chart.utils = {
	color: function(index) {
	    return COLORS[index % COLORS.length];
	},
	
	generateData: function(count) {
	
	    var min = 0;
	    var max = 100;
	    var dfactor = 10;
	    
	    var data = [];
	    
	    for (i = 0; i < count; ++i) {
		value = Math.random() * max;     
		data.push(Math.round(dfactor * value) / dfactor);
		
	    }
	    return data;
	},
    }

}(this));
