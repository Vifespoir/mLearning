"""Advanced visualization of attributes."""
import pandas as pd
from bokeh.palettes import brewer, Inferno9
from random import uniform
import matplotlib.colors as colors
import matplotlib.cm as cmax
from mLearning.bokehPlot import BokehPlot
# from bokehPlot import BokehPlot
import logging
import concurrent.futures
from time import clock
from bokeh.embed import file_html
from bokeh.resources import CDN
import dill
from pathos.multiprocessing import ProcessingPool

__all__ = ('DataPlot')

logging.basicConfig(
    level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')


# TODO run test on other datasets
# TODO add more assertion and try/except clauses
# TODO TODO get rid of matplotlib dependancy

DATA_INDEX = 'name'


class DataPlot():
    """Child class from dataStatistics to plot interesting data."""
    logging.debug('DataPlot class instantiated.')

    def __init__(self, tableName, dataFile, normalized):
        """Initialize DataPlot."""
        self.tableName = tableName
        self.dataFile = dataFile
        self.data = pd.read_csv(self.dataFile)
        self.data = self.concatenate_dates()
        self.data = self.clean_column_text(DATA_INDEX)
        self.data = self.set_index(DATA_INDEX)
        self.description = self.data.describe()
        self.numericData = self.data.select_dtypes(include=['float64'])
        self.currentData = self.numericData
        self.summary = self.data.describe()
        self.normalized = normalized
        if normalized:
            self.normalize_data()

    def clean_column_text(self, col):
        logging.debug('Cleaning "{}" column'.format(col))
        column = self.data[col]
        column.replace({'([^A-zÀ-ÿ]+|[À-ÿ$]+)': ' '}, regex=True, inplace=True)
        column = column.str.strip()
        column.replace({'\s+': '_'}, regex=True, inplace=True)
        self.data[col] = column
        print(set(self.data[col]))
        return self.data

    def set_index(self, col):
        logging.debug('Set "{}" column as index'.format(col))
        self.data.set_index(col, inplace=True)
        return self.data

    def boxplot_all_quartiles(self):  # works
        """Plot all normalized quartiles."""

        title = "Quartile Ranges"
        data = self.currentData
        # Prepare a new, simpler data frame with only attributes and their values
        data = data.stack()  # Stack data to get one attribute value per line
        newData = []
        for d in data.items():
            newData.append([d[0][1], d[1]])  # Select the attribute and its value

        newData = pd.DataFrame(newData, columns=['attribute', 'value'])
        lines = {'line': dict(data=newData, bokehType='BoxPlot', values='value',
                              label='attribute', title=title)}
        fig = BokehPlot('boxplot_all_quartiles', lines)  # pyflakes:ignore:E0602

        logging.debug('Boxplot generated')
        return fig  # return the boxplot graph for html generation

    def parallel_coordinates_graph(self):  # works
        """Open a parallel coordinates graph of the attributes."""
                # TODO Add plot element to generate CategoricalTi

        title = 'parallel_coordinates_graph'
        data = self.currentData
        indexes = [x for x in set(self.data.index)]

        colorMap = cmax.viridis
        cNorm = colors.Normalize(vmin=0, vmax=len(indexes)-1)
        scalarMap = cmax.ScalarMappable(norm=cNorm, cmap=colorMap)

        lines = {}
        for i in range(len(indexes)):
            colorVal = scalarMap.to_rgba(i)
            colorVal = colors.rgb2hex(colorVal)
            indexLines = len(data.loc[indexes[i]].values)
            xs = [list(range(len(data.columns)))]*indexLines
            ys = [list(v) for v in data.loc[indexes[i]].values]
            lines[indexes[i]] = dict(x=xs, y=ys, line_color=colorVal, bokehType='multi_line')

        fig = BokehPlot(title, lines, interactive=True)
        logging.debug('Parallel coordinates graph generated')
        return fig

    def heatmap_pearson_correlation(self):  # works
        """Create a heatmap of attributes."""

        data = self.currentData

        data = data.corr(method='pearson')
        title = 'heatmap_pearson_correlation'

        values = []
        for v in list(data.values):
            values.extend(v)

        x, y = [], []
        for c in list(data.columns):
            x.extend([c]*len(data.index))
            y.append(c)

        y = y * len(data.columns)
        data = {'x': x, 'y': y, 'values': values}
        lines = {'line': dict(data=data, x='x', y='y', values='values',
                              bokehType='HeatMap', title=title, stat=None, palette=Inferno9)}
        fig = BokehPlot(title, lines)

        logging.debug('Heatmap of Pearson correalation generated')
        return fig  # return the boxplot graph for html generation

    def cross_plotting_pair_of_attributes(self, firstCol, secondCol):  # works
        """Open a a graph of correlated pairs of attributes."""

        title = 'cross_plotting_pair_of_attributes'
        lines = {}
        lines = {'line': dict(data=self.data, x=firstCol, y=secondCol,
                              bokehType='Scatter', title=title)}
        fig = BokehPlot(title, lines)

        logging.debug('Pair of attribute crossplotted')
        return fig  # return the boxplot graph for html generation

    def plot_target_correlation(self, col):  # works
        """Open a graph of attribute and its target attribute."""
        # TODO display attribute names on x axis

        attributes = set(self.data.index)
        increment, i, attributesDict = 1 / len(attributes), 0, {}
        for attribute in attributes:
            attributesDict[attribute] = i
            i += increment

        targetValues = []
        for i in self.data.index:
            # add some dither
            targetValues.append(attributesDict[i] + uniform(-0.1, 0.1))

        title = 'plot_target_correlation' + ':  ' + col
        lines = {}
        data = pd.DataFrame(list(zip(targetValues, self.data[col].values)), columns=['Attribute Value', 'Target Value'])
        lines['line'] = dict(data=data, x='Attribute Value', y='Target Value', bokehType='Scatter', title=title)
        fig = BokehPlot(title, lines)

        logging.debug('Target correlation plotted')
        return fig  # return the boxplot graph for html generation

    def normalize_data(self):
        """Normalize columns to improve graphical representations."""

        self.normalizedData = self.numericData.copy()
        for i in range(len(self.normalizedData.columns)):
            mean = self.description.iloc[1, i]
            std_dev = self.description.iloc[2, i]
            self.normalizedData.iloc[:, i:(i+1)] = (self.normalizedData.iloc[:, i:(i+1)] - mean) / std_dev

        logging.debug('Data normalized')
        self.currentData, self.normalized = self.normalizedData, True

    def denormalize_data(self):
        """Denormalize columns."""
        self.currentData, self.normalized = self.numericData, False
        logging.debug('Data denormalized')

    def concatenate_dates(self):
        """Concatenate year, month, day into a date, fill month, day if needed."""

        data = self.data
        try:
            data['day']
        except KeyError:  # set day to 1
            data['day'] = pd.Series([1]*len(data.index), index=data.index)

        try:
            data['month']
        except KeyError:  # set day to 1
            data['month'] = pd.Series([1]*len(data.index), index=data.index)

        try:
            data['year']
        except KeyError:  # set day to 1
            assert data['date'], 'ERROR: No date available in dataset.'

        dataDate = data[['year', 'month', 'day']].astype(int)  # select date related columns
        dataDate = pd.to_datetime(dataDate)
        data['date'] = pd.Series(dataDate, index=data.index)
        data.drop(['year', 'month', 'day'], axis=1, inplace=True)

        logging.debug('Dates concatenated')

        return data

    def create_transposed_plot(self, name, dataset):

        name = name.replace('/ ', '_').replace('/', ' ')  # correct encoding error
        dataset = dataset.select_dtypes(include=['float64', 'datetime64'])
        dataset = dataset.sort_values('date')
        dataset = dataset.transpose()
        # years, months = mdates.YearLocator(), mdates.MonthLocator()
        colors = brewer['Paired'][len(dataset.index)]  # generate color palette
        lines = {}
        for i, color in zip(dataset.index, colors):  # associate colors with index
            if i != 'date':  # ignore date row
                lines[i] = dict(x=list(dataset.loc['date']), y=list(dataset.loc[i]),
                                bokehType='line', legend=i, color=color)

        logging.debug('Transposed plot created')

        plot = BokehPlot(name, lines, figProp=dict(x_axis_type='datetime', title=name))

        html = file_html(plot.document(), CDN)

        return html, plot.plotName

    def transpose_index(self):  # WORKS ONLY FOR TEST DATA
        """Transpose the data according to the index."""

        data = self.data
        indexes = list(set(data.index))

        names, datasets = [], []
        for name in indexes:
            names.append(name)
            datasets.append(data[[name in i for i in data.index]])

        plotSets = zip(names, datasets)

        pool = ProcessingPool()
        plots = []
        for name, dataset in plotSets:
            plots.append(pool.map(self.create_transposed_plot, [name], [dataset]))

        logging.debug('Index transposed')

        return plots

if __name__ == '__main__':
    start = clock()
    # logger = logging.getLogger()
    # logger.setLevel(logging.ERROR)
    dataFile = '/home/vifespoir/github/mLearningApp/mLearning/data/US/veggies-imp.csv'
    plots = DataPlot('us-veggies', dataFile, False)
    plots = plots.transpose_index()
    print('Runtime to transpose_index: {:.2f} second(s)'.format(clock() - start))
    # plots.boxplot_all_quartiles(normalized=True)
    # plots.boxplot_all_quartiles(normalized=False)
    # plots.plot_target_correlation('vol')
    # plots.cross_plotting_pair_of_attributes('vol', 'val')
    # plots.heatmap_pearson_correlation(normalized=True)
    # plots.parallel_coordinates_graph(normalized=True)
