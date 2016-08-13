from bokeh.plotting import figure, output_file, show
from bokeh.models import CheckboxGroup, CustomJS
from bokeh.layouts import row
from bokeh import charts
import re

# TODO seperate simple graphs from complex one with child class

MINIMUM_GRAPH_PROPERTIES = ['x', 'y']
LINE_NAME_PATTERN = '\w\d+'
BOKEH_TYPE = 'bokehType'

class BokehPlot(object):
    """docstring for """
    def __init__(self, plotName, lines, interactive=False):
        self.plotName, self.lines = plotName, lines
        assert isinstance(plotName, str), 'plotName is not a string'
        assert isinstance(lines, dict), 'lines is not a dictionary'
        self.fig = figure()
        self.interactive = interactive

    def _visible_line_JS(self, line):
        return """
        if ({0} in checkbox.active) {{
        {1}.visible = true
        }} else {{
        {1}.visible = false
        }}
        """.format(int(line[1:]), line)

    def plot_figure(self):
        output_file(self.plotName + '.html', title=self.plotName)
        lines, index = {}, 0
        for lineName, line in self.lines.items():
            print(line.keys())
            if 'data' in line.keys():
                graphData = line.pop('data')
            else:
                graphData = []
                for prop in MINIMUM_GRAPH_PROPERTIES:
                    assert prop in line.keys(), 'missing property: %s' % prop
                    graphData.append(line.pop(prop))

            assert BOKEH_TYPE in line.keys(), 'missing property: %s' % BOKEH_TYPE
            methodName = line.pop(BOKEH_TYPE)
            print(methodName)
            print(line.keys())
            error = False
            try:
                method = getattr(self.fig, methodName)
                lines[lineName] = method(*graphData, **line)
            except AttributeError:
                error = self.fig.__class__.__name__
                try:
                    method = getattr(charts, methodName)
                    print(line)
                    print(type(line))
                    self.fig = method(graphData, values=line['values'], label=line['label'], title=line['title'])
                except AttributeError:
                    error = charts.__class__.__name__
                else:
                    error = False

            if error:
                raise NotImplementedError("Class '{}' does not implement '{}'".format(error, methodName))

            print('graphData\n\n', type(graphData))
            print('line\n\n', line)
            index += 1

        return lines

    def interactive_figure(self):
        lines = self.plot_figure()
        lineNames = ['l'+str(x) for x in range(len(lines))]
        lines = {k: v for k, v in zip(lineNames, lines.values())}

        JScode = [self._visible_line_JS(k) for k in lines]
        JScode = '\n'.join(JScode)

        callback = CustomJS(code=JScode, args={})
        checkbox = CheckboxGroup(labels=[i for i in self.lines.keys()],
                                 active=list(range(len(lines))),
                                 callback=callback)
        lines['checkbox'] = checkbox
        callback.args = lines
        layout = row(self.fig, checkbox)

        return layout

    def show(self):
        if self.interactive:
            show(self.interactive_figure())
        else:
            self.plot_figure()
            show(self.fig)
