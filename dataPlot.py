"""Advanced visualization of attributes."""

import numpy as np
import pandas as pd

from pandas import DataFrame
from pandas.tools.plotting import parallel_coordinates

import matplotlib.pyplot as plt
import matplotlib.dates as  mdates
import matplotlib.colors as colors
import matplotlib.cm as cmax

from bokeh.plotting import figure
from bokeh import mpl
from bokeh.charts import BoxPlot
from bokeh.plotting import output_file, show

import pylab
import scipy.stats as stats

import sys
from datetime import date

from mLearning.interactivePlotClasses import AxesSequence, AxesVisibility

# TODO let user choose a column to plot colors
# TODO pick what to be displayed from legend


class DataPlot():
    """Child class from dataStatistics to plot interesting data."""

    def __init__(self, tableName, dataFile):
        """Initialize dataplt."""
        self.tableName = tableName
        self.dataFile = dataFile
        self.data = pd.read_csv(self.dataFile, index_col='name')
        # self.set_col_to_categorical()
        print(self.data.columns)
        print(self.data.index)
        self.description = self.data.describe()
        self.numericData = self.data.select_dtypes(include=['float64'])
        self.normalize_data()
        self.summary = self.data.describe()

    def boxplot_all_quartiles(self, normalized=False):
        """Plot all normalized quartiles."""
        title = "Quartile Ranges"
        if normalized:
            title = title + "- Normalized"
            data = self.normalizedData
        else:
            data = self.numericData

        # Prepare a new, simpler data frame with only attributes and their values
        data = data.stack() # Stack data to get one attribute value per line
        newData = []
        for d in data.items():
            newData.append([d[0][1], d[1]]) # Select the attribute and its value

        newData =  DataFrame(newData, columns=['attribute', 'value'])
        graph = BoxPlot(newData, values='value', label='attribute', title=title)

        return graph # return the boxplot graph for html generation

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

        fig = axes.show()

        return fig

    def cross_plotting_pairs_of_attributes(self, firstCol, secondCol):
        """Open a a graph of correlated pairs of attributes."""
        firstData = self.data[firstCol]
        secondData = self.data[secondCol]

        plt.scatter(firstData, secondData)
        plt.xlabel(self.data[firstCol].name)
        plt.ylabel(self.data[secondCol].name)

        output_file("cross_plotting_pairs_of_attributes.html", title="cross_plotting_pairs_of_attributes")
        show(mpl.to_bokeh())

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
        output_file("plot_target_correlation.html", title="plot_target_correlation")
        show(mpl.to_bokeh())

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
        output_file("plot_pearson_correlation.html", title="plot_pearson_correlation")
        show(mpl.to_bokeh())

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

        fig = axes.show()

        # self.transposedData = self.data.transpose()

        return fig


if __name__ == '__main__':
    dataFile = '/home/vifespoir/github/mLearningApp/mLearning/data/US/veggies-exp.csv'
    plots = DataPlot('us-veggies', dataFile)
    # plots.print_head_and_tail()
    # plots.print_summary_of_data()
    # plots.data = plots.transpose_index()
    # plots.parallel_coordinates_graph(normalized=False)
    # plots.plot_quartiles('val')
    plots.boxplot_all_quartiles(normalized=True)
    # plots.boxplot_all_quartiles(normalized=True)
    # plots.plot_target_correlation('vol')
    # plots.cross_plotting_pairs_of_attributes('vol', 'val')
    # plots.plot_pearson_correlation()
