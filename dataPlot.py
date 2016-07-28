"""Advanced visualization of attributes."""

import numpy as np
import pandas as pd

from pandas import DataFrame
from pandas.tools.plotting import parallel_coordinates

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.dates as  mdates
import matplotlib.colors as colors
import matplotlib.cm as cmax
from matplotlib import gridspec

import pylab
import scipy.stats as stats

import sys
from dataStatistics import TableData
from datetime import date

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

    def parallel_coordinates_graph(self, normalized=False):
        """Open a parallel coordinates graph of the attributes."""
        if normalized:
            data = self.NormalizedData
        else:
            data = self.numericData

        indexes = [x for x in set(self.data.index)]
        colorMap = plt.get_cmap('Paired')
        cNorm  = colors.Normalize(vmin=0, vmax=len(indexes)-1)
        scalarMap = cmax.ScalarMappable(norm=cNorm, cmap=colorMap)

        ylim = (min(data.min(numeric_only=True)), max(data.max(numeric_only=True)))
        axes = AxesVisibility(axeNames=indexes, ylim=ylim) # works with numeric indexes
        handlesLabels = []
        for i, ax in zip(range(len(indexes)), axes):
            colorVal = scalarMap.to_rgba(i)
            for value in data.loc[indexes[i]].values:
                ax.plot(range(len(data.columns)), value, color=colorVal, label=indexes[i])

        axes.axes[0].set_title('Click on legend line to toggle line on/off')
        axes.axes[0].set_xlabel("Attribute Index")
        axes.axes[0].set_ylabel("Attribute Values")

        axes.show()

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
        self.NormalizedData = self.numericData.copy()
        for i in range(len(self.NormalizedData.columns)):
            mean = self.description.iloc[1, i]
            std_dev = self.description.iloc[2, i]
            self.NormalizedData.iloc[:, i:(i+1)] = (self.NormalizedData.iloc[:, i:(i+1)] - mean) / std_dev

    def transpose_index(self):
        """Transpose the data according to the index."""
        indexes = list(set(self.data.index))
        i = 1
        axes = AxesSequence()
        for index, ax in zip(indexes, axes):
            data = self.data.loc[index].select_dtypes(include=['float64'])
            data = data.sort(['year', 'month'], ascending=[1, 1])
            print(data.head())
            data = data.transpose()
            print(data.head())
            zipDate = zip(data.loc['year'], data.loc['month'])
            dateList = [date(int(x), int(y), 1) for x, y in zipDate]
            print(dateList)
            years, months = mdates.YearLocator(), mdates.MonthLocator()
            for i in ['val', 'vol', 'unit_value']:
                ax.plot(dateList, data.loc[i].values, label=i)
                ax.set_title(index, size=30)
                ax.xaxis.set_major_locator(months)
                ax.xaxis.set_minor_locator(years)
                ax.set_xticklabels(dateList, rotation=90)
                ax.legend()
        axes.show()

        return self.data.transpose()


class AxesSequence(object):
    """Creates a series of axes in a figure where only one is displayed at any
    given time. Which plot is displayed is controlled by the arrow keys."""
    def __init__(self):
        self.fig = plt.figure()
        self.axes = []
        self._i = 0 # Currently displayed axes index
        self._n = 0 # Last created axes index
        self.fig.canvas.mpl_connect('key_press_event', self.on_keypress)

    def __iter__(self):
        while True:
            yield self.new()

    def new(self):
        # The label needs to be specified so that a new axes will be created
        # instead of "add_axes" just returning the original one.
        ax = self.fig.add_axes([0.15, 0.1, 0.8, 0.8], visible=False, label=self._n)
        self._n += 1
        self.axes.append(ax)
        return ax

    def on_keypress(self, event):
        if event.key == 'right':
            self.next_plot()
        elif event.key == 'left':
            self.prev_plot()
        else:
            return
        self.fig.canvas.draw()

    def next_plot(self):
        if self._i < len(self.axes):
            self.axes[self._i].set_visible(False)
            self.axes[self._i+1].set_visible(True)
            self._i += 1

    def prev_plot(self):
        if self._i > 0:
            self.axes[self._i].set_visible(False)
            self.axes[self._i-1].set_visible(True)
            self._i -= 1

    def show(self):
        self.axes[0].set_visible(True)
        plt.show()


class AxesVisibility(object):
    def __init__(self, axeNames, xlim=False, ylim=False):
        self.fig = plt.figure(figsize=(16,9))
        # self.graph = self.fig.add_subplot(gridspec.GridSpec(2, 1, height_ratios=[3, 1])[0])
        self.axeNames = axeNames
        self.axes = []
        self._n = 0 # Last created axes index
        self.xlim = xlim
        self.ylim = ylim
        self.legendAxe = self.make_legend_axe()
        # axes.fig.legend.get_frame().set_alpha(0.4)

    def __iter__(self):
        while True:
            yield self.new()

    def make_legend_axe(self):
        ax = self.fig.add_axes([0.05, 0.35, 0.9, 0.60], frameon=False, label='legend')

        if self.xlim:
            ax.set_xlim(self.xlim[0], self.xlim[1])
        if self.ylim:
            ax.set_ylim(self.ylim[0], self.ylim[1])

        return ax

    def new(self):
        # The label needs to be specified so that a new axes will be created
        # instead of "add_axes" just returning the original one.
        ax = self.legendAxe.twiny().twinx()
        ax.grid(b=False)
        ax.get_xaxis().set_ticks([])
        ax.get_yaxis().set_ticks([])
        ax.set_label(self.axeNames[self._n])
        self._n += 1
        self.axes.append(ax)
        return ax

    def generate_legend(self):
        handles = []
        for ax in self.axes:
            for line in ax.get_lines():
                handles.append((line, line.get_label()))
                break

        toggleLabel = 'Hide All'
        handles.append((mlines.Line2D([], [], label=toggleLabel), toggleLabel))
        handles, labels = zip(*handles)
        legend = self.legendAxe.legend(handles, labels, bbox_to_anchor=(0.1, -0.4, 0.9, 0.30), ncol=5)

        lined, axes = {}, self.axes
        axes.append(None)
        for legLine, legAxe in zip(legend.get_lines(), axes):
            legLine.set_picker(5)  # 5 pts tolerance
            print(legLine.get_label())
            if legLine.get_label() == toggleLabel:
                lined[legLine] = False
                print(lined[legLine])
            else:
                lined[legLine] = legAxe

        def on_pick(event):
            # on the pick event, find the orig line corresponding to the
            # legend proxy line, and toggle the visibility
            legLine = event.artist
            print(legLine)
            legAxe = lined[legLine]

            togglePop = [k for k, v in lined.items() if v == True or v == False][0]
            toggleStatus = lined.pop(togglePop)

            print('Status', toggleStatus)

            if legAxe is True:
                toggleStatus = not toggleStatus
                for line, axe in lined.items():
                    is_visible = True
                    axe.set_visible(is_visible)
                    line.set_alpha(1.0)
            elif legAxe is False:
                toggleStatus = not toggleStatus
                for line, axe in lined.items():
                    is_visible = False
                    axe.set_visible(is_visible)
                    line.set_alpha(0.2)
            else:
                is_visible = not legAxe.get_visible()
                legAxe.set_visible(is_visible)

            lined[togglePop] = toggleStatus

            if is_visible:
                legLine.set_alpha(1.0)
            else:
                legLine.set_alpha(0.2)
            self.fig.canvas.draw()

        self.fig.canvas.mpl_connect('pick_event', on_pick)

    def show(self):
        self.generate_legend()
        plt.show()


if __name__ == '__main__':
    dataFile = '/home/vifespoir/github/mLearning/data/US/veggies-exp.csv'
    plots = dataPlot('us-veggies', dataFile)
    # plots.print_head_and_tail()
    # plots.print_summary_of_data()
    # plots.data = plots.transpose_index()
    plots.parallel_coordinates_graph(normalized=False)
    # plots.plot_quartiles('val')
    # plots.boxplot_all_quartiles(normalized=False)
    # plots.boxplot_all_quartiles(normalized=True)
    # plots.plot_target_correlation('vol')
    # plots.cross_plotting_pairs_of_attributes('vol', 'val')
    # plots.plot_pearson_correlation()
