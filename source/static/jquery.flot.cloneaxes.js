(function ($) {
	function init(plot) {
		plot.cloneAxes = function (templatePlot) {
			var options = templatePlot.getOptions();
			var targetOptions = plot.getOptions();
			var targetAxes = plot.getAxes();
			var props = ['xaxis', 'yaxis'];

			console.log(options);

			plot.getOptions().xaxes = templatePlot.getOptions().xaxes;
			plot.getOptions().yaxes = templatePlot.getOptions().yaxes;

			console.log(targetOptions);

			//plot.setupGrid();
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