FROM octoprint/octoprint
WORKDIR /usr/src/fractal
COPY . .
RUN pip3 install . --upgrade
