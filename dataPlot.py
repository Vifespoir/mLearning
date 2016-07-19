"""Advanced visualization of attributes."""

import numpy as np
import pandas as pd
from pandas import DataFrame
from pandas.tools.plotting import parallel_coordinates
import matplotlib.pyplot as plot
import pylab
import scipy.stats as stats
import sys
from dataStatistics import TableData
from random import uniform

# TODO let user choose a column to plot colors
# TODO pick what to be displayed from legend

class dataPlot():
    """Child class from dataStatistics to plot interesting data."""

    def __init__(self, tableName, dataFile):
        """Initialize dataPlot."""
        self.tableName = tableName
        self.dataFile = dataFile
        self.data = self.read_csv()
        self.set_col_to_categorical()
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
        plot.boxplot(array)
        plot.xlabel("Attribute Index")
        plot.ylabel(yLabel)
        x = np.array(range(len(self.numericData.columns) + 1))
        print(self.numericData.columns)
        plot.xticks(x, self.numericData.columns.insert(0, ''))
        plot.show()


    def read_csv(self):
        """Read a csv file."""
        data = pd.read_csv(self.dataFile)
        return data

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
        print(self.data.dtypes)

    def parallel_coordinates_graph(self):
        """Open a parallel coordinates graph of the attributes."""
        attributes = self.data['name'].cat.categories
        print('parallel_coordinates_graph attributes: ', attributes)
        increment, i, attributesDict = 1 / len(attributes), 0, {}
        for attribute in attributes:
            print(attribute)
            attributesDict[attribute] = i
            i += increment

        print(self.data.index)

        targetValue = []
        for i in self.data.index:
            targetValue.append(self.data.iloc[i, 1:])

        data = self.data.ix[:, 1:]
        print(data)
        plot.figure()
        parallel_coordinates(data, 'name')
        plot.xlabel("Attribute Index")
        plot.ylabel("Attribute Values")
        plot.legend(loc='lower center')
        plot.show()

    def cross_plotting_pairs_of_attributes(self, firstCol, secondCol):
        """Open a a graph of correlated pairs of attributes."""
        firstData = self.data[firstCol]
        secondData = self.data[secondCol]

        plot.scatter(firstData, secondData)
        plot.xlabel(self.data[firstCol].name)
        plot.ylabel(self.data[secondCol].name)

        plot.show()

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

        plot.scatter(self.data[col], targetValues, alpha=0.5, s=120)

        plot.xlabel('Attribute Value')
        plot.ylabel('Target Value')
        plot.show()

    def plot_pearson_correlation(self, normalized=False):
        """Create a heatmap of attributes."""
        if normalized:
            data = self.numericData
        else:
            data = self.oldNumericData

        corrDataFrame = DataFrame().corr(data)

        plot.pcolor(corrDataFrame)
        plot.show()

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
    # plots.parallel_coordinates_graph()
    # plots.plot_quartiles('val')
    # plots.boxplot_all_quartiles(normalized=False)
    # plots.boxplot_all_quartiles(normalized=True)
    # plots.plot_target_correlation('vol')
    # plots.cross_plotting_pairs_of_attributes('vol', 'val')
    # plots.plot_pearson_correlation()
