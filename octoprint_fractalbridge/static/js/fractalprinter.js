$(function() {
    function FractalPrinterViewModel(parameters) {
        var self = this;

        self.settings = parameters[0];

        self.pluginName = "FractalPrinter";

        self.connectToFractal = function () {
            var url = window.PLUGIN_BASEURL + self.pluginName + '/connect'
            // var url = 'http://localhost:5000/plugin/FractalPrinter/connect'
            $.ajax(url);
        };

        self.resetDB = function () {
            var url = window.PLUGIN_BASEURL + self.pluginName + '/reset_db'
            // var url = 'http://localhost:5000/plugin/FractalPrinter/connect'
            $.ajax(url);
        };
    }

    OCTOPRINT_VIEWMODELS.push([
        FractalPrinterViewModel,
        ["settingsViewModel"],
        ["#settings_plugin_FractalPrinter"]
    ]);
});
