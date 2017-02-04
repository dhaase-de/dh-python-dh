"""
Tools for data visualization.
"""

import abc
import json
import textwrap

import dh.utils


###
#%% Google charts wrapper
###


class GoogleCharts():
    """
    Wrapper for Google charts (https://developers.google.com/chart/).

    This class creates a "container" to which multiple charts (instances of
    class `GoogleChart` can be added (see :func:`GoogleCharts.append()`.
    """

    def __init__(self, api="current"):
        self._api = api
        self.charts = []

    @property
    def api(self):
        return self._api

    def append(self, chart):
        """
        Append chart to this Google charts object.
        """

        if not isinstance(chart, GoogleChart):
            raise TypeError("Argument 'chart' must be of type 'GoogleChart' (but '{}' was provided)".format(type(chart)))
        if chart.uid is None:
            chart.uid = "{:>04d}".format(len(self.charts))
        self.charts.append(chart)

    def renderJs(self):
        """
        Returns string of the JavaScript code which draws all charts of this.
        """

        template = """
            <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
            <script type="text/javascript">
                //google.charts.load('current', {{'packages':['corechart']}});
                google.charts.load({api}, {{'packages':['corechart']}});
                google.charts.setOnLoadCallback(drawAllCharts);

                {functions}

                function drawAllCharts() {{
                    {functionCalls}
                }}
            </script>
        """

        return textwrap.dedent(template).format(
            api=json.dumps(self.api),
            functions="\n".join(chart.renderFunctionJs() for chart in self.charts),
            functionCalls="\n".join("{}();".format(chart.functionName()) for chart in self.charts),
        )

    def renderDivs(self):
        """
        Returns string of the HTML `div` elements needed to draw the charts.
        """
        return "\n".join("<div id=\"{}\"></div>".format(chart.divName()) for chart in self.charts)

    def renderHtml(self):
        template = """
            <html>
                <head>
                    {js}
                    <style>
                        body {{
                            background-color: #EEE;
                            text-align: center;
                        }}
                        div.chart {{
                            margin: 50px auto;
                        }}
                    </style>
                </head>
                <body>
                    {divs}
                </body>
            </html>
        """

        return textwrap.dedent(template).format(
            js=self.renderJs(),
            divs=self.renderDivs(),
        )

    def save(self, filename):
        dh.utils.mkpdir(filename)
        with open(filename, "w") as f:
            f.write(self.renderHtml())


class GoogleChart(abc.ABC):
    """
    Base class for individual Google charts which can be added to a
    `GoogleCharts` container.
    """

    def __init__(self, uid=None, options=None):
        self._uid = uid
        if options is not None:
            self._options = options
        else:
            self._options = {}
        self._header = []
        self._data = []

    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, value):
        self._uid = value

    ##
    ##
    ##

    @property
    def header(self):
        return self._header

    @header.setter
    def header(self, value):
        if value is not None:
            self._header = [value]
        else:
            self._header= []

    @property
    def data(self):
        return self._data

    ##
    ## options
    ##

    @property
    def options(self):
        return self._options

    @property
    def title(self):
        try:
            return self.options["title"]
        except KeyError:
            return None

    @title.setter
    def title(self, value):
        self.options["title"] = str(value)

    ##
    ## rendering
    ##

    @staticmethod
    @abc.abstractmethod
    def chartClass():
        pass

    @staticmethod
    def renderObject(obj):
        """
        Render Python object `obj` as Javascript object.
        """
        return json.dumps(obj, indent=4, sort_keys=True)

    def functionName(self):
        return "chart_{uid}_draw".format(uid=self.uid)

    def divName(self):
        return "chart_{uid}_div".format(uid=self.uid)

    def renderFunctionJs(self):
        template = """
            function {functionName}() {{
                var data = google.visualization.arrayToDataTable({data});

                var options = {options};

                var chart = new {chartClass}(document.getElementById('{divName}'));
                chart.draw(data, options);
            }}
        """

        return textwrap.dedent(template).format(
            functionName=self.functionName(),
            data=self.renderObject(self.header + self.data),
            options=self.renderObject(self.options),
            chartClass=self.chartClass(),
            divName=self.divName(),
        )


class GoogleColumnChart(GoogleChart):
    """
    Column chart which can be added to a `GoogleCharts` container.

    .. note:: Use `collections.OrderedDict` to order the labels.
    """

    def __init__(self, xs, yss, **kwargs):
        super().__init__(**kwargs)

        # header
        labeled = isinstance(yss, dict)
        if labeled:
            ulabels = tuple(dh.utils.unique(yss.keys()))
            self.header = ("x",) + ulabels
        else:
            self.header = ("x", "y")

        # data
        rowCount = len(xs)
        for nRow in range(rowCount):
            if labeled:
                row = [xs[nRow]] + [yss[label][nRow] for label in ulabels]
            else:
                row = (xs[nRow], yss[nRow])
            self._data.append(row)

    @staticmethod
    def chartClass():
        return "google.visualization.ColumnChart"


class GoogleScatterChart(GoogleChart):
    """
    Scatter chart which can be added to a `GoogleCharts` container.
    """

    def __init__(self, xs, ys, labels=None, **kwargs):
        super().__init__(**kwargs)

        # header
        labeled = (labels is not None)
        if labeled:
            ulabels = tuple(dh.utils.unique(labels))
            labelCount = len(ulabels)
            self.header = ("x",) + ulabels
        else:
            self.header = ("x", "y")

        # data
        rowCount = len(xs)
        for nRow in range(rowCount):
            if labeled:
                row = [None] * (labelCount + 1)
                row[0] = xs[nRow]
                row[ulabels.index(labels[nRow]) + 1] = ys[nRow]
            else:
                row = (xs[nRow], ys[nRow])
            self._data.append(row)

    @staticmethod
    def chartClass():
        return "google.visualization.ScatterChart"


class GoogleLineChart(GoogleChart):
    """
    Line chart which can be added to a `GoogleCharts` container.

    `xs` must be a iterable specifying the x values of the chart. `yss` must be
    either an iterable or a dictionary of iterables. If `yss` is an iterable,
    the chart will have one line with y values according to `yss`. If `yss` is
    a dictionary of iterables, the chart will have multiple lines, where the
    y values are given by each iterable of the dictionary. The dictionary keys
    will then serve as labels.

    .. note:: Use `collections.OrderedDict` to order the labels.
    """

    def __init__(self, xs, yss, **kwargs):
        super().__init__(**kwargs)

        # header
        labeled = isinstance(yss, dict)
        if labeled:
            ulabels = tuple(dh.utils.unique(yss.keys()))
            self.header = ("x",) + ulabels
        else:
            self.header = ("x", "y")

        # data
        rowCount = len(xs)
        for nRow in range(rowCount):
            if labeled:
                row = [xs[nRow]] + [yss[label][nRow] for label in ulabels]
            else:
                row = (xs[nRow], yss[nRow])
            self._data.append(row)

    @staticmethod
    def chartClass():
        return "google.visualization.LineChart"


if __name__ == "__main__":
    c = GoogleCharts()
    c.append(GoogleScatterChart([1, 2, 3, 4], [2, 3, 2, 1], ["a", "a", "b", "b"]))
    c.append(GoogleLineChart([1, 2, 3, 4], [2, 3, 2, 1]))
    c.append(GoogleLineChart([1, 2, 3, 4], {"a": [2, 3, 2, 1], "b": [3, 2, 2, 4]}))
    c.save("/home/dh/tmp/chart.html")
