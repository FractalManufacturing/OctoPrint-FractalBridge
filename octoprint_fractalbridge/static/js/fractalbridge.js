$(function() {
    function FractalBridgeViewModel(parameters) {
        var self = this;

        self.settings = parameters[0];

        self.pluginName = "fractalbridge";

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
        FractalBridgeViewModel,
        ["settingsViewModel"],
        ["#settings_plugin_fractalbridge"]
    ]);
});
