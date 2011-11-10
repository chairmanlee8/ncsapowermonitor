(function ($) {
	function init(plot) {
		plot.cloneAxes = function (templatePlot) {
			var options = templatePlot.getOptions();
			var axes = templatePlot.getAxes();
			var targetOptions = plot.getOptions();
			var targetAxes = plot.getAxes();
			var props = ['xaxis', 'yaxis'];

			for(var k in props)
			{
				if(!targetAxes[props[k]].used) continue;

				console.log(axes[props[k]].min);
				console.log(targetOptions[props[k]].min);

				targetOptions[props[k]].min = axes[props[k]].min;
				targetOptions[props[k]].max = axes[props[k]].max;

				console.log(targetOptions[props[k]].min);
				console.log("done");
			}

			plot.setupGrid();
			plot.draw();
		}
	}

	$.plot.plugins.push({
		init: init,
		options: {},
		name: 'navigate',
		version: '1.0'
	});
})(jQuery);