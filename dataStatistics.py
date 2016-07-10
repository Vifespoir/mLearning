import numpy
import logging
from pprint import pformat
from sys import stdout
import pylab
import scipy.stats as stats


logging.basicConfig(
    level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')


class Constants:
    """Class for constants."""
    self.type = 'Column Type'
    self.float = 'Percent of Float Entries'
    self.mean = 'Mean'
    self.stdDev = 'Standard Deviation'
    self.quantiles = 'Quantile Boundaries'
    self.ID = 'id'
    self.labels = 'Unique Labels (with count)'


class tableData:
    """Contain whole table information."""

    def __init__(self, tableName, tableData, tableFields):
        self.tableName = tableName
        self.tableData = tableData
        self.tableFields = tableFields
        self.colInfo = {}
        self.tableColumns = self.generate_cols()
        self.colToDelete = []

    def generate_cols(self, threshold=0.9):
        """Generate column lists."""
        columns = {}
        for field in self.tableFields:
            self.colInfo[field] = {}
            iType = [0]*3
            for row in self.tableData:
                try:
                    row[field] = row[field].replace('$', '', 1).replace(',', '').strip()
                    row[field] = float(row[field])
                    iType[0] += 1
                except ValueError:
                    if len(row[field]) > 1:
                        iType[1] += 1
                    else:
                        iType[2] += 1

            self.colInfo[field][Constants.float] = iType[0]/sum(iType) + iType[2]/sum(iType)

            if iType[0]/sum(iType) + iType[2]/sum(iType) >= threshold:
                for row in self.tableData:
                    if not isinstance(row[field], float) and len(row[field]) <= 1:
                        row[field] = 0

                    columns.setdefault(field, [])
                    columns[field].append(row[field])
                    colType = float

            else:
                for row in self.tableData:
                    if len(row[field]) <= 1:
                        row[field] = None
                    colType = str
                    columns.setdefault(field, [])
                    columns[field].append(row[field])

            self.colInfo[field][Constants.type] = colType

        return columns

    def get_col(self, columnName):
        return self.tableColumns.get(columnName)

    def show_col_info(self):
        """Show columns info and assist in making decision about each column."""
        graphs = self.choose('Do you want to see graphs?')
        for col in self.tableColumns:
            stdout.write('Column Name:   "%s"\n' % col)
            stdout.write(pformat(self.colInfo[col]))
            if graphs and self.choose('Do you want to see "%s" graph?' % col):
                self.plot_col()
            self.rename_col(col)


    def transform_col_into_numpy_array(self):
        """Calculate the mean variance for a given column."""
        for field in self.tableFields:
            colType = self.colInfo[field][Constants.type]
            if colType is float:
                colArray = numpy.array(self.tableColumns[field])
                self.tableColumns[field] = colArray
                self.colInfo[field][Constants.mean] = numpy.mean(colArray)
                self.colInfo[field][Constants.StdDev] = numpy.std(colArray)

                percentiles = [4, 10]
                for n in percentiles:
                    quantileName = Constants.quantiles + ' for %s percentiles' % n
                    bdries = self.calc_quantile_boundaries(colArray, n)
                    bdriesStr = ' - '.join(['{:.2f}'.format(p) for p in bdries])
                    self.colInfo[field][quantileName] = bdriesStr

    def calc_quantile_boundaries(self, ntiles=[4, 10]):
        """Calculate quantile boundaries for a given column."""
        percentBdry = {}
        for key in self.tableArrays:
            for n in ntiles:
                for i in range(ntiles+1):
                    percentBdry[n] = numpy.percentile(self.tableArrays[key], i*100/ntiles)

        return percentBdry

    def find_categories(self):
        """Find all the possible categories for a column."""
        for col in self.tableColumns:
            uniqueData = set(self.tableColumns[col])

            catDict = {k: 0 for k in uniqueData}

            for elt in self.tableColumns[col]:
                catDict[elt] += 1

            catPrint = {k: v for k, v in catDict.items() if v > 2}

            if self.colInfo[col][Constants.type] is float:
                if len(set([v for v in catDict.values()])) <= 1:
                    self.colToDelete.append(col)

            elif len(catPrint) <= 1 and col != Constants.ID:
                self.colToDelete.append(col)

            else:
                self.colInfo[col][Constants.label] = catPrint

    def plot_col(self, field):
        """Plot the data of a column."""
        graph = input('Look at "{:10}" quantile distribution? (y/n)  '
                      .format(field))
        if graph == 'y' or graph == 'Y':
            stats.probplot(self.tableColumns[field], dist="norm", plot=pylab)
            pylab.show()
            break
        elif graph == 'n' or graph == 'N':
            break
        else:
            print('Please enter "y" or "n":  ')

    def rename_col(self, col):
        """Rename columns."""
        newName = {}
        if self.choose('Do you want to rename "%s"?' % col):
            newName = input('Enter new column name:')
            try:
                self.tableData[newName] = self.tableData.pop(col)
                self.tableColumns[newName] = self.tableColumns.pop(col)
                self.colToDelete[self.colToDelete.index(col)] = newName
            except KeyError as e:
                logging.warning("Trying to rename a column that doesn't exist: %s" % e)

    def delete_columns_check(self):
        """Store data after both manual and autnatic sorting."""
        iCol = 0
        while self.choose('Do you want to keep one of these columns?'):
            for c in self.colToDelete:
                stdout.write(str(iCol) + ' - ' + c + '\n')
                iCol += 1
            stdout.write(str(iCol) + ' - if you changed your mind\n')
            while True:
                try:
                    iCol = int(input('Column index, enter: 0-%s   \n' % str(len(self.colToDelete)+1)))
                    if iCol == len(self.colToDelete) + 1:
                        break
                    elif iCol in range(0, len(self.colToDelete)):
                        self.colToDelete.pop(iCol)
                        break
                except ValueError:
                    stdout.write('Enter a valid input.\n')

        for c in self.colToDelete:
            logging.info('Deleting: %s' % c)
            try:
                self.tableFields.remove(c)
                self.tableData.pop(c)
                self.tableColumns.pop(c)
            except KeyError as e:
                logging.warning("Trying to delete a column that doesn't exist: %s" % e)

    def choose(text):
        """Allow user to make choices returns boolean."""
        while True:
            response = input(text + '  (y/n)  ')
            if response == 'y' or response == 'Y':
                return True
            elif response == 'n' or response == 'N':
                return False
            else:
                print('Please enter "y" or "n":  ')


if __name__ == '__main__':
    tableName = input('Enter table name:   ')
    table = tableData(tableName, data, headers)
