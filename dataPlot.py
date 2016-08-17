"""Advanced visualization of attributes."""

import numpy as np
import pandas as pd

from pandas import DataFrame
from pandas.tools.plotting import parallel_coordinates

import matplotlib.pyplot as plt
import matplotlib.dates as  mdates
import matplotlib.colors as colors
import matplotlib.cm as cmax

import pylab
import scipy.stats as stats

import sys
from dataStatistics import TableData
from datetime import date

from interactivePlotClasses import AxesSequence, AxesVisibility

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
            data = self.normalizedData
        else:
            data = self.numericData
            print(data)

        indexes = [x for x in set(self.data.index)]
        colorMap = plt.get_cmap('Paired')
        cNorm  = colors.Normalize(vmin=0, vmax=len(indexes)-1)
        scalarMap = cmax.ScalarMappable(norm=cNorm, cmap=colorMap)

        axes = AxesVisibility(axeNames=indexes, columns=data.columns) # works with numeric indexes see for loop

        for i, ax in zip(range(len(indexes)), axes):
            colorVal = scalarMap.to_rgba(i)
            for value in data.loc[indexes[i]].values:
                ax.plot(range(len(data.columns)), value, color=colorVal, label=indexes[i])

            ylim, ylimLegend = ax.get_ylim(), list(axes.legendAxe.get_ylim())
            if ylim[0] < ylimLegend[0]:
                ylimLegend[0] = ylim[0]
            if ylim[1] > ylimLegend[1]:
                ylimLegend[1] = ylim[1]
            axes.legendAxe.set_ylim(ylimLegend)

        for ax in axes.axes:
            ax.set_ylim(axes.legendAxe.get_ylim())

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
            data = self.normalizedData
        else:
            data = self.numericData

        corrDataFrame = DataFrame(data).corr()

        plt.pcolor(corrDataFrame)
        x = np.array([r - 0.5 for r in range(1, len(self.numericData.columns) + 1)])
        plt.xticks(x, self.numericData.columns)
        plt.yticks(x, self.numericData.columns)
        plt.show()

    def normalize_data(self):
        """Normalize columns to improve graphical representations."""
        self.normalizedData = self.numericData.copy()
        for i in range(len(self.normalizedData.columns)):
            mean = self.description.iloc[1, i]
            std_dev = self.description.iloc[2, i]
            self.normalizedData.iloc[:, i:(i+1)] = (self.normalizedData.iloc[:, i:(i+1)] - mean) / std_dev

    def transpose_index(self):
        """Transpose the data according to the index."""
        indexes = list(set(self.data.index))
        i = 1
        axes = AxesSequence()
        for index, ax in zip(indexes, axes):
            data = self.data.loc[index].select_dtypes(include=['float64'])
            data = data.sort(['year', 'month'], ascending=[1, 1])
            data = data.transpose()
            zipDate = zip(data.loc['year'], data.loc['month'])
            dateList = [date(int(x), int(y), 1) for x, y in zipDate]
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


if __name__ == '__main__':
    dataFile = '/home/vifespoir/github/mLearningApp/mLearning/data/US/veggies-exp.csv'
    plots = dataPlot('us-veggies', dataFile)
    # plots.print_head_and_tail()
    # plots.print_summary_of_data()
    # plots.data = plots.transpose_index()
    # plots.parallel_coordinates_graph(normalized=False)
    # plots.plot_quartiles('val')
    # plots.boxplot_all_quartiles(normalized=False)
    # plots.boxplot_all_quartiles(normalized=True)
    # plots.plot_target_correlation('vol')
    # plots.cross_plotting_pairs_of_attributes('vol', 'val')
    plots.plot_pearson_correlation()
