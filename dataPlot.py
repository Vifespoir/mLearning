"""Advanced visualization of attributes."""

import numpy as np
import pandas as pd

from pandas import DataFrame
from pandas.tools.plotting import parallel_coordinates

import matplotlib.pyplot as plt
import matplotlib.dates as  mdates
import matplotlib.colors as colors
import matplotlib.cm as cmax

from bokeh.charts import BoxPlot
from bokehPlot import BokehPlot
from bokeh.palettes import brewer

import pylab
import scipy.stats as stats

import sys
from datetime import date

from interactivePlotClasses import AxesSequence, AxesVisibility

from random import uniform

__all__ = ['DataPlot']
# TODO let user choose a column to plot colors

class DataPlot():
    """Child class from dataStatistics to plot interesting data."""

    def __init__(self, tableName, dataFile):
        """Initialize dataplt."""
        self.tableName = tableName
        self.dataFile = dataFile
        self.data = pd.read_csv(self.dataFile, index_col='name')
        # self.set_col_to_categorical()
        # print(self.data.columns)
        # print(self.data.index)
        self.description = self.data.describe()
        self.numericData = self.data.select_dtypes(include=['float64'])
        self.normalize_data()
        self.summary = self.data.describe()

    def boxplot_all_quartiles(self, normalized=False): # works
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
        lines['line'] = dict(data=newData, bokehType='BoxPlot', values='value', label='attribute', title=title)
        fig = BokehPlot('boxplot_all_quartiles', lines)
        fig.show()
        return fig # return the boxplot graph for html generation

    def parallel_coordinates_graph(self, normalized=False): # works
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

        lines = {}
        for i in range(len(indexes)):
            colorVal = scalarMap.to_rgba(i)
            colorVal = colors.rgb2hex(colorVal)
            indexLines = len(data.loc[indexes[i]].values)
            xs = [list(range(len(data.columns)))]*indexLines
            ys = [list(v) for v in data.loc[indexes[i]].values]
            lines[indexes[i]] = dict(xs=xs, ys=ys, line_color=colorVal, bokehType='multi_line')

        fig = BokehPlot('parallel_coordinates_graph', lines, interactive=True)
        fig.show()
        return fig

    def cross_plotting_pairs_of_attributes(self, firstCol, secondCol): # works
        """Open a a graph of correlated pairs of attributes."""
        title = 'cross_plotting_pairs_of_attributes'
        lines = {}
        lines['line'] = dict(data=self.data, x=firstCol, y=secondCol, bokehType='Scatter', title=title)
        fig = BokehPlot(title, lines)
        fig.show()
        return fig # return the boxplot graph for html generation

    def plot_target_correlation(self, col): # works
        """Open a graph of attribute and its target attribute."""
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
        data = DataFrame(list(zip(targetValues, self.data[col].values)), columns=['Attribute Value', 'Target Value'])
        lines['line'] = dict(data=data, x='Attribute Value', y='Target Value', bokehType='Scatter', title=title)
        fig = BokehPlot(title, lines)
        fig.show()
        return fig # return the boxplot graph for html generation

    def plot_pearson_correlation(self, normalized=False): # underwork
        """Create a heatmap of attributes."""
        if normalized:
            data = self.numericData
        else:
            data = self.oldNumericData

        data = DataFrame(data).corr()

        # x = np.array([r - 0.5 for r in range(1, len(self.numericData.columns) + 1)])
        # plt.xticks(x, self.numericData.columns)
        # plt.yticks(x, self.numericData.columns)
        title = 'plot_pearson_correlation'
        lines = {}
        # TODO find equivalent to pcolor in Bokeh
        lines['line'] = dict(data=data, bokehType='', title=title)
        fig = BokehPlot(title, lines)
        fig.show()
        return fig # return the boxplot graph for html generation

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
        lines = {}
        for index in indexes:
            name = index.replace('/ ', '_').replace('/', ' ')
            data = self.data.loc[index].select_dtypes(include=['float64'])
            data['day'] = pd.Series([1]*len(data.index), index=data.index)
            dataDate = data[['year', 'month', 'day']].astype(int)
            dataDate = pd.to_datetime(dataDate)
            data['date'] = pd.Series(dataDate, index=data.index)
            for item in ['year', 'month', 'day']:
                data.pop(item)
            data = data.sort_values('date')
            data = data.transpose()
            # years, months = mdates.YearLocator(), mdates.MonthLocator()
            colors = brewer['Paired'][len(data.index)]
            for i, color in zip(data.index, colors):
                if i != 'date':
                    lines[i] = dict(x=list(data.loc['date']), y=list(data.loc[i]), bokehType='line', legend=i, color=color)
            # ax.xaxis.set_major_locator(months)
            # ax.xaxis.set_minor_locator(years)
            # ax.set_xticklabels(dateList, rotation=90)
            # ax.legend()
            fig = BokehPlot(name, lines, figProp=dict(x_axis_type='datetime', title=index))
            fig.save()


if __name__ == '__main__':
    dataFile = '/home/vifespoir/github/mLearningApp/mLearning/data/US/veggies-exp.csv'
    plots = DataPlot('us-veggies', dataFile)
    # plots.print_head_and_tail()
    # plots.print_summary_of_data()
    plots.data = plots.transpose_index()
    # plots.parallel_coordinates_graph(normalized=True)
    # plots.plot_quartiles('val')
    # plots.boxplot_all_quartiles(normalized=True)
    # plots.boxplot_all_quartiles(normalized=False)
    # plots.plot_target_correlation('vol')
    # plots.cross_plotting_pairs_of_attributes('vol', 'val')
    # plots.plot_pearson_correlation()
