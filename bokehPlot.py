"""Helper module to build Bokeh plots."""
from bokeh.plotting import figure, output_file, show, save
from bokeh.models import CustomJS, CheckboxGroup
from bokeh.layouts import row, widgetbox
from bokeh import charts
from bokeh.models.widgets import Button
from bokeh.embed import components
import logging
from os import getcwd
from os.path import join as osjoin

logging.basicConfig(
    level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

__all__ = ('BokehPlot')


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

    def plot_figure(self):
        """Construct the figure."""
        logging.debug('Plotting figure...')

        output_file('BokehHTML/' + self.plotName + '.html', title=self.plotName)
        lines, index = {}, 0
        for lineName, line in self.lines.items():
            if 'data' in line.keys():
                graphData = line.pop('data')
            else:
                graphData = []
                for prop in MINIMUM_GRAPH_PROPERTIES:
                    assert prop in line.keys(), 'missing property: "%s"' % prop
                    graphData.append(line.pop(prop))

            assert BOKEH_TYPE in line.keys(), 'missing property: {}, properties: {}'.format(BOKEH_TYPE, line.keys())
            methodName = line.pop(BOKEH_TYPE)
            error = False
            try:
                method = getattr(self.fig, methodName)
            except AttributeError:
                error = self.fig.__class__.__name__
                try:
                    method = getattr(charts, methodName)
                except AttributeError:
                    error = charts.__class__.__name__
                else:
                    error = False
                    self.fig = method(graphData, **line)
            else:
                lines[lineName] = method(*graphData, **line)

            if error:
                raise NotImplementedError("Class '{}' does not implement '{}'".format(error, methodName))
            index += 1

        logging.debug('Figure plotted.')
        return lines

    def _visible_line_JS(self, line):
        """Generate JavaScript code for Bokeh client side, not public.

        Toggle visibility of individual line."""
        # logging.debug('Generating JavaScript to toggle line visibility...')  # Optional -- too many prints

        return """if ({0} in checkbox.active) {{
        {1}.visible = true
        }} else {{
        {1}.visible = false}}""".format(int(line[1:]), line)
        logging.debug('JavaScript generated.')

    def interactive_figure(self):
        """Add interactivity, ie. the option to show/hide lines to the figure."""
        logging.debug('Implementing interaction to figure...')

        lines = self.plot_figure()  # Generates a list of lines
        labels = [line for line in lines.keys()]  # Prepare a list of labels for the tickboxes
        lineNames = ['l'+str(x) for x in range(len(lines))] # Prepare a list of names for the lines
        lines = {k: v for k, v in zip(lineNames, lines.values())}  # Create a dictionary {name: line}
        activeL = list(range(len(lines)))  # List of all line index to mark them as active in CheckboxGroup

        JScode = [self._visible_line_JS(k) for k in lines]  # Generate JavaScript for each line
        JScode = '\n'.join(JScode)  # From a list to a single string

        with open(osjoin(getcwd(), 'mLearning', 'JScodeAllLines.js'), 'r') as fileJS:
            buttonJS = fileJS.read()  # Read JavaScript code from a file to toggle the visibility of all lines
        # with open(osjoin(getcwd(), 'mLearning', 'JScode.js'), 'w+') as codeFile:
        #     codeFile.write(JScode)  # Write whole CustomJS to a file for debugging purposes

        callback = CustomJS(code=JScode, args={})  # Args will be added once checkbox and button are added to lines
        checkbox = CheckboxGroup(labels=labels,
                                 active=activeL,  # Labels to be ticked from the beginning
                                 callback=callback,
                                 name='checkbox')  # JavaScript var name

        buttonCallback = CustomJS(code=buttonJS, args={})  # Same as for callback
        button = Button(label="Select/Unselect All",  # Button HTML text
                        button_type="default",
                        callback=buttonCallback,
                        name='button')  # JavaScript var name

        lines['checkbox'], lines['button'] = checkbox, button  # Adding widget to lines
        callback.args, buttonCallback.args = lines, lines  # And then lines to callback
        layout = row(self.fig, widgetbox(children=[button, checkbox], width=200))  # One row, two columns

        logging.debug('Interaction implemented.')
        return layout

    def document(self):
        """Return a Bokeh document object to be rendered."""
        logging.debug('Returning document...')
        if self.interactive:
            interactive_figure = self.interactive_figure()
            save(interactive_figure, filename=SAVE_FOLDER + self.plotName)
            return interactive_figure
        else:
            self.plot_figure()
            save(obj=self.fig, filename=SAVE_FOLDER + self.plotName)
            return self.fig
        logging.debug('Document returned.')

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
