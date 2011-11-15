(function ($) {
	function init(plot) {
		plot.cloneAxes = function (templatePlot) {
			var templateAxes = templatePlot.getAxes();
			$.each(plot.getAxes(), function(idx, axis)
			{
				axis.options.min = templateAxes[idx].options.min;
				axis.options.max = templateAxes[idx].options.max;
			});

			plot.setupGrid();
			plot.draw();
		}

		plot.reloadMarkings = function (newMarkings) {
			plot.options.grid.markings = newMarkings;
			
			plot.setupGrid();
			plot.draw();
		}
	}

	$.plot.plugins.push({
		init: init,
		options: {},
		name: 'cloneaxes',
		version: '1.0'
	});
})(jQuery);