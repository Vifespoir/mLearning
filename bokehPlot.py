"""Helper module to build Bokeh plots."""
from bokeh.plotting import figure, output_file, show, save
from bokeh.models import CheckboxGroup, CustomJS
from bokeh.layouts import column, row
from bokeh import charts
import logging

logging.basicConfig(
    level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

__all__ = ('BokehPlot')

# TODO seperate simple graphs from complex one with child class

MINIMUM_GRAPH_PROPERTIES = ['x', 'y']
LINE_NAME_PATTERN = '\w\d+'
BOKEH_TYPE = 'bokehType'
SAVE_FOLDER = 'BokehHTML/'


class BokehPlot(object):
    """Helper class to generate Bokeh plots."""
    logging.debug('BokehPlot class instantiated.')

    def __init__(self, plotName, lines, figProp={}, interactive=False):
        """Initialize BokehPlot."""
        self.plotName, self.lines = plotName, lines
        assert isinstance(plotName, str), 'plotName is not a string'
        assert isinstance(lines, dict), 'lines is not a dictionary'
        self.fig = figure(**figProp)
        self.interactive = interactive

    def _visible_line_JS(self, line):
        """Generate JavaScript code for Bokeh client side, not public.

        Toggle visibility of individual line."""
        logging.debug('Generating JavaScript to toggle line visibility...')

        return """
                if ({0} in checkbox1.active) {{
                {1}.visible = true
                }} else {{
                {1}.visible = false
                }}
                """.format(int(line[1:]), line)
        logging.debug('JavaScript generated.')

    def _visible_all_lines_JS(self, lines, buttonIndex):
        """Generate JavaScript code for Bokeh client side, not public.

        Toggle visibility of all lines."""
        logging.debug('Generating JavaScript to toggle all lines visibility...')

        ifStatement = "if ({0} in checkbox2.active) {{\n".format(buttonIndex)
        elseStatement = "else {\n"
        endStatement = "}\n"
        lineTrue, lineFalse = [], []
        for line in lines:
            lineTrue.append("{}.visible = true\n".format(line))
            lineFalse.append("{}.visible = false\n".format(line))
        lineTrue, lineFalse = ''.join(lineTrue), ''.join(lineFalse)

        JScode = ifStatement + lineTrue + endStatement + elseStatement+ lineFalse + endStatement

        logging.debug('JavaScript generated.')
        print(JScode)
        return JScode

    def plot_figure(self):
        """Construct the figure."""
        logging.debug('Plotting figure...')

        output_file('BokehHTML/' + self.plotName + '.html', title=self.plotName)
        lines, index = {}, 0
        for lineName, line in self.lines.items():
            # print(line.keys())
            if 'data' in line.keys():
                graphData = line.pop('data')
            else:
                graphData = []
                for prop in MINIMUM_GRAPH_PROPERTIES:
                    assert prop in line.keys(), 'missing property: "%s"' % prop
                    graphData.append(line.pop(prop))

            assert BOKEH_TYPE in line.keys(), 'missing property: %s' % BOKEH_TYPE
            methodName = line.pop(BOKEH_TYPE)
            # print(methodName)
            # print(line.keys())
            error = False
            try:
                method = getattr(self.fig, methodName)
                # logging.debug('METHOD 1: %s' % method)
            except AttributeError:
                error = self.fig.__class__.__name__
                logging.debug('ERROR 1: %s' % error)
                try:
                    method = getattr(charts, methodName)
                    # logging.debug('METHOD 2: %s' % method)
                except AttributeError:
                    error = charts.__class__.__name__
                    logging.debug('ERROR 2: %s' % error)
                else:
                    error = False
                    self.fig = method(graphData, **line)
                    logging.debug('ERROR 3: %s' % error)
            else:
                lines[lineName] = method(*graphData, **line)

            if error:
                raise NotImplementedError("Class '{}' does not implement '{}'".format(error, methodName))
            index += 1

        logging.debug('Figure plotted.')
        return lines

    def interactive_figure(self):
        """Add interactivity, ie. the option to show/hide lines to the figure."""
        logging.debug('Implementing interaction to figure...')

        lines = self.plot_figure()
        lineNames = ['l'+str(x) for x in range(len(lines))]
        lines = {k: v for k, v in zip(lineNames, lines.values())}

        labels = [i for i in self.lines.keys()]
        JScode = [self._visible_line_JS(k) for k in lines]
        JScode = '\n'.join(JScode)
        activeL = list(range(len(lines)))
        print(JScode)

        buttonIndex, buttonLabel = 0, 'All Lines'
        JScodeAllLines = self._visible_all_lines_JS(lines, buttonIndex)

        callback1 = CustomJS(code=JScode, args={})
        checkbox1 = CheckboxGroup(labels=labels,
                                  active=activeL,
                                  callback=callback1,
                                  name='checkbox1')

        callback2 = CustomJS(code=JScodeAllLines, args={})
        checkbox2 = CheckboxGroup(labels=[buttonLabel],
                                  active=[buttonIndex],
                                  callback=callback2,
                                  name='checkbox2')

        lines['checkbox1'] = checkbox1
        lines['checkbox2'] = checkbox2
        callback1.args = lines
        callback2.args = lines
        layout = row(self.fig, checkbox1, checkbox2)

        logging.debug('Interaction implemented.')
        return layout

    def document(self):
        """Return a Bokeh document object to be rendered."""
        logging.debug('Returning figure...')
        if self.interactive:
            interactive_figure = self.interactive_figure()
            save(interactive_figure, filename=SAVE_FOLDER + self.plotName)
            return interactive_figure
        else:
            self.plot_figure()
            save(obj=self.fig, filename=SAVE_FOLDER + self.plotName)
            return self.fig
        logging.debug('Figure returned.')

    def show(self):
        """Show the figure in the browser (works locally)."""
        logging.debug('Showing figure...')
        show(self.document())
        logging.debug('Figure shown.')

    def save(self):
        logging.debug('Saving figure...')

        """Save the figure at the specified location."""
        if self.interactive:
            interactive_figure = self.interactive_figure()
            save(interactive_figure, filename=SAVE_FOLDER + self.plotName)
        else:
            self.plot_figure()
            save(obj=self.fig, filename=SAVE_FOLDER + self.plotName)

        logging.debug('Figure saved.')
