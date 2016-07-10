import numpy
import logging
from pprint import pformat
from sys import stdout
import pylab
import scipy.stats as stats

# TODO triple choice for rename and keep
# TODO find out why val and vol don't appear
# TODO exclude rescued columns from showing up with automatically kept columns


logging.basicConfig(
    level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')


class ColInfoConstants:
    """Class for constants."""

    def __init__(self):
        """Initialize constants."""
        self.colType = 'Column Type'
        self.colFloat = 'Percent of Float Entries'
        self.colMean = 'Mean'
        self.colStdDev = 'Standard Deviation'
        self.colQuantiles = 'Quantile Boundaries'
        self.ID = 'id'
        self.colLabels = 'Unique Labels (with count)'


class TableData:
    """Contain whole table information."""

    def __init__(self, tableName, tableData, tableFields):
        """Initialize tableData."""
        self.Constants = ColInfoConstants()
        self.tableName = tableName
        self.tableData = tableData
        self.tableFields = tableFields
        self.colInfo = {}
        self.tableColumns = self.generate_cols()
        self.colToDelete = []
        self.find_categories()

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

            self.colInfo[field][self.Constants.colFloat] = iType[0]/sum(iType) + iType[2]/sum(iType)

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

            self.colInfo[field][self.Constants.colType] = colType

        return columns

    def get_col(self, columnName):
        """Get the specified column."""
        return self.tableColumns.get(columnName)

    def get_col_names(self):
        """Get the specified column."""
        return self.tableFields

    def show_col_info(self, field, graphs):
        """Show columns info and assist in making decision about each column."""
        stdout.write('\nColumn Name:   "%s"\n' % field)
        stdout.write(pformat(self.colInfo[field])+'\n')
        if graphs and self.colInfo[field][self.Constants.colType] is not str\
                and self.choose('Do you want to see "%s" graph?' % field):
            self.plot_col(field)
        if self.keep_col(field):
            self.rename_col(field)

    def start_analysis(self):
        """Start the data analysis."""
        logging.info('Rescuing columns to be automatically deleted...')
        graphs = self.choose('Do you want to see graphs?')
        for field in self.colToDelete:
            self.show_col_info(field, graphs)
        logging.info('Checking columns to be automatically kept...')
        graphs = self.choose('Do you want to see graphs?')
        for field in self.tableFields:
            self.show_col_info(field, graphs)

    def transform_col_into_numpy_array(self):
        """Calculate the mean variance for a given column."""
        for field in self.tableFields:
            colType = self.colInfo[field][self.Constants.colType]
            if colType is float:
                colArray = numpy.array(self.tableColumns[field])
                self.tableColumns[field] = colArray
                self.colInfo[field][self.Constants.colMean] = numpy.mean(colArray)
                self.colInfo[field][self.Constants.colStdDev] = numpy.std(colArray)

                percentiles = [4, 10]
                for n in percentiles:
                    quantileName = self.Constants.colQuantiles + ' for %s percentiles' % n
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

            catPrint = {k: v for k, v in catDict.items() if v > 1}
            self.colInfo[col][self.Constants.colLabels] = catPrint
            if self.colInfo[col][self.Constants.colType] is float:
                if len(set([v for v in catDict.values()])) <= 1:
                    self.colToDelete.append(col)

            elif len(catPrint) <= 1 and col != self.Constants.ID:
                self.colToDelete.append(col)

    def plot_col(self, field):
        """Plot the data of a column."""
        stats.probplot(self.tableColumns[field], dist="norm", plot=pylab)
        pylab.show()

    def rename_col(self, field):
        """Rename columns."""
        newName = {}
        if self.choose('Do you want to rename "%s"?' % field):
            newName = input('Enter new column name:')
            try:
                for row in self.tableData:
                    row[newName] = row.pop(field)
                self.tableColumns[newName] = self.tableColumns.pop(field)
                self.tableFields[self.tableFields.index(field)] = newName
                self.colInfo[newName] = self.colInfo.pop(field)
                try:
                    self.colToDelete[self.colToDelete.index(field)] = newName
                except ValueError:
                    pass
            except KeyError as e:
                logging.warning("Trying to rename a column that doesn't exist: %s" % e)

    def keep_col(self, field):
        """Store data after both manual and autnatic sorting."""
        if self.choose('Do you want to keep "%s" column?' % field):
            try:
                self.colToDelete.remove(field)
            except ValueError:
                pass
            logging.info('Keeping: %s' % field)

            return True

        else:
            logging.info('Deleting: %s' % field)
            try:
                self.tableFields.remove(field)
                for row in self.tableData:
                    row.pop(field)
                self.tableColumns.pop(field)
                self.colInfo.pop(field)
            except KeyError as e:
                logging.warning("Trying to delete a column that doesn't exist: %s" % e)

            return False

    def choose(self, text):
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
