"""Advanced visualization of attributes."""

import numpy as np
import pandas as pd
from pandas import DataFrame
from pandas.tools.plotting import parallel_coordinates
import matplotlib.pyplot as plt
from matplotlib.colors import cnames
import matplotlib.lines as mlines
from matplotlib.artist import Artist
from matplotlib import gridspec
import pylab
import scipy.stats as stats
import sys
from dataStatistics import TableData
from random import choice

# TODO let user choose a column to plot colors
# TODO pick what to be displayed from legend


class dataPlot():
    """Child class from dataStatistics to plot interesting data."""

    def __init__(self, tableName, dataFile):
        """Initialize dataplt."""
        self.tableName = tableName
        self.dataFile = dataFile
        self.data = pd.read_csv(self.dataFile, index_col='name')
        # self.set_col_to_categorical()
        print(self.data.dtypes)
        print(self.data.columns)
        self.description = self.data.describe()
        self.numericData = self.data.select_dtypes(include=['float64'])
        self.normalize_data()

    def plot_quartiles(self, col):
        """Open a quantile representation of an attribute."""
        stats.probplot(self.data[col], dist="norm", plot=pylab)
        pylab.show()

    def boxplot_all_quartiles(self, normalized=False):
        """Plot all normalized quartiles."""
        yLabel = "Quartile Ranges"
        if normalized:
            array = self.numericData.values
            yLabel = yLabel + "- Normalized"
        else:
            array = self.oldNumericData.values
        plt.boxplot(array)
        plt.xlabel("Attribute Index")
        plt.ylabel(yLabel)
        x = np.array(range(1, len(self.numericData.columns) + 1))
        plt.xticks(x, self.numericData.columns)
        plt.show()

    def print_head_and_tail(self):
        """Print the head and tail of a dataset."""
        print(self.data.head())
        print(self.data.tail())

    def print_summary_of_data(self):
        """Print a summary of the data."""
        print(self.data.describe())

    def set_col_to_categorical(self):
        """Get a list of attribute for a given column."""
        for i in self.data.columns:
            if i != 'id':
                if self.data[i].dtype == 'object':
                    self.data[i] = self.data[i].astype('category')
                    print('Column type for "%s" hanged' % i)

    def parallel_coordinates_graph(self):
        """Open a parallel coordinates graph of the attributes."""

        # print(self.data['name'].cat.categories)
        # for i in self.data.index:
        #     if 'Artichokes' == self.data.loc[i,'name']:
        #         print(self.data.iloc[i,:])
        # print(self.data.head())
        # print(self.data.loc['Artichokes'])
        # print(self.data.columns)
        data = self.data.iloc[:, 1:]
        colorset = {}
        colors = [c for c in cnames.keys()]
        for name in set(data.index):
            color = choice(colors)
            while color in [v for v in colorset.values()]:
                color = choice(colors)
            colorset[name] = color
        # print(colorset)

        i = 1
        fig = plt.figure(figsize=(16,8))
        dataCat = {}
        legendHandles = []
        gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
        graph = fig.add_subplot(gs[0])
        for key in colorset:
            dataCat[key] = []
            i += 1
            # # print(data.loc[key])
            # print(data.columns)
            for value in data.loc[key].values:
                # print(value)
                dataCat[key] += graph.plot(range(1, len(data.columns) + 1), value, color=colorset[key])

            legendHandles.append(mlines.Line2D([], [], color=colorset[key], label=key))

        graph.set_title('Click on legend line to toggle line on/off')
        leg = graph.legend(handles=legendHandles, prop={'size':'small'}, bbox_to_anchor=(0, -0.2), loc=2, borderaxespad=0, ncol=5)
        leg.get_frame().set_alpha(0.4)

        for key in dataCat:
            graph.lines.extend(dataCat[key])

        # data = data.ix[:1, 1:]
        # figure, ax = plt.subplots()
        graph.set_xlabel("Attribute Index")
        graph.set_ylabel("Attribute Values")
        x = np.array(range(0, len(self.numericData.columns)))
        graph.set_xticklabels(self.numericData.columns)
        # InteractiveGraph(figure, ax)
        displayedLines = dict()
        print(len(leg.get_lines()))
        # print(fig)
        # print(dataCat.values())
        for legendLine in leg.get_lines():
            # lines = dataCat[legendLine.get_label()]
            legendLine.set_picker(5)  # 5 pts tolerance
            print(legendLine.get_picker())
            # displayedLines[legendLine] = lines
        print('before canvas')
        fig.canvas.mpl_connect('pick_event', lambda event: self.on_pick(event, [fig, dataCat]))
        print('after canvas')
        plt.show()

    def on_pick(self, event, arg_list):
        # on the pick event, find the orig line corresponding to the
        # legend proxy line, and toggle the visibility
        fig, dataCat = arg_list
        legendLine = event.artist
        lines = dataCat[legendLine.get_label()]
        print('printing len lines', len(lines))
        for line in lines:
        # print('is_visible before', originLine.get_visible())
            is_visible = not line.get_visible()
        # print('is_visible after', is_visible)
            line.set_visible(is_visible)
        # Change the alpha on the line in the legend so we can see what lines
        # have been toggled
        if is_visible:
            legendLine.set_alpha(1.0)
        else:
            legendLine.set_alpha(0.2)

        fig.canvas.draw()

    def cross_plotting_pairs_of_attributes(self, firstCol, secondCol):
        """Open a a graph of correlated pairs of attributes."""
        firstData = self.data[firstCol]
        secondData = self.data[secondCol]

        plt.scatter(firstData, secondData)
        plt.xlabel(self.data[firstCol].name)
        plt.ylabel(self.data[secondCol].name)

        plt.show()

    def plot_target_correlation(self, col):
        """Open a graph of attribute and its target attribute."""
        attributes = self.data['name'].cat.categories
        increment, i, attributesDict = 1 / len(attributes), 0, {}
        for attribute in attributes:
            attributesDict[attribute] = i
            i += increment

        targetValues = []
        for i in self.data.index:
            # add some dither
            targetValues.append(attributesDict[self.data.iloc[i, 1]] + uniform(-0.1, 0.1))

        plt.scatter(self.data[col], targetValues, alpha=0.5, s=120)

        plt.xlabel('Attribute Value')
        plt.ylabel('Target Value')
        plt.show()

    def plot_pearson_correlation(self, normalized=False):
        """Create a heatmap of attributes."""
        if normalized:
            data = self.numericData
        else:
            data = self.oldNumericData

        corrDataFrame = DataFrame(data).corr()

        plt.pcolor(corrDataFrame)
        x = np.array([r - 0.5 for r in range(1, len(self.numericData.columns) + 1)])
        plt.xticks(x, self.numericData.columns)
        plt.yticks(x, self.numericData.columns)
        plt.show()

    def normalize_data(self):
        """Normalize columns to improve graphical representations."""
        self.oldNumericData = self.numericData.copy()
        for i in range(len(self.numericData.columns)):
            mean = self.description.iloc[1, i]
            std_dev = self.description.iloc[2, i]
            self.numericData.iloc[:, i:(i+1)] = (self.numericData.iloc[:, i:(i+1)] - mean) / std_dev


if __name__ == '__main__':
    dataFile = '/home/vifespoir/github/mLearning/data/US/veggies-exp.csv'
    plots = dataPlot('us-veggies', dataFile)
    # plots.print_head_and_tail()
    # plots.print_summary_of_data()
    plots.parallel_coordinates_graph()
    # plots.plot_quartiles('val')
    # plots.boxplot_all_quartiles(normalized=False)
    # plots.boxplot_all_quartiles(normalized=True)
    # plots.plot_target_correlation('vol')
    # plots.cross_plotting_pairs_of_attributes('vol', 'val')
    # plots.plot_pearson_correlation()
