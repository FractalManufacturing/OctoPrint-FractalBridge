FROM gastonmaffei/octoprint

ENV PIP_USER false

RUN pip install "https://github.com/SimplyPrint/OctoPrint-Creality2xTemperatureReportingFix/archive/master.zip"
RUN pip install "https://github.com/FractalManufacturing/OctoPrint-FractalBridge/archive/master.zip"

COPY config.yaml /octoprint/octoprint/config.yaml

RUN octoprint -b /octoprint/octoprint user add --password Fractal --admin Fractal

RUN octoprint -b /octoprint/octoprint user list

VOLUME /octoprint