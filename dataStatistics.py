"""Module to understand and select interesting columns from row data."""

import numpy
import logging
from pprint import pformat
from sys import stdout
import pylab
import scipy.stats as stats
from random import choice

# TODO find out why val and vol don't appear
# TODO order columns in menu

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
        self.colLabelsInfo = 'Info'


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
        self.colKept = []

    def generate_cols(self, threshold=0.9):
        """Generate column lists and associated statistics."""
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

    def column_menu(self):
        """Display a menu and let the user choose on which column he wants to work."""
        stdout.write('{:>2}-{:>20}  {:>10}  {:>10}  {:>10}\n'
                     .format('#', 'Column name', 'Type', 'Quality', 'Status'))
        iCol = 0
        easyAccess = {}
        for field in self.tableFields:
            easyAccess[iCol] = field
            colType = self.colInfo[field][self.Constants.colType]
            colPercent = self.colInfo[field][self.Constants.colFloat]
            if colType is not float:
                colType = 'String'
                colPercent = 1 - colPercent
            else:
                colType = 'Numeric'

            if field in self.colToDelete:
                colStatus = 'DELETE'
            else:
                colStatus = 'KEEP'
            stdout.write('{:>2}-{:>20}  {:>10}  {:>.2%}  {:>10}\n'
                         .format(iCol, field[:19], colType, colPercent, colStatus))
            iCol += 1

        return easyAccess

    def show_col_info(self, field, graphs):
        """Show columns info and assist in making decision about each column."""
        stdout.write('\nColumn Name:   "%s"\n' % field)
        stdout.write(pformat(self.colInfo[field])+'\n')
        if graphs and self.colInfo[field][self.Constants.colType] is not str\
                and self.choose('Do you want to see "%s" graph?' % field):
            self.plot_col(field)
        stdout.write('What do you want to do?\n')
        stdout.write('1 - keep the column\n')
        stdout.write('2 - keep and rename the column\n')
        stdout.write('3 - delete the column\n')
        while True:
            choice = input('Your choice, 1-3:   ')
            if choice == '1':
                self.keep_col(field, True)
                break
            elif choice == '2':
                self.keep_col(field, True)
                self.rename_col(field)
                break
            elif choice == '3':
                self.keep_col(field, False)
                break
            else:
                stdout.write('Wrong input.\n')

    def start_analysis(self):
        """Start the data analysis."""
        if self.choose('Manual inspection?'):
            graphs = self.choose('Do you want to see graphs?')
            colAccess = self.column_menu()
            while True:
                colNumber = input('Enter a column number: ("q" to exit)  ')
                if colNumber == "q":
                    break
                else:
                    field = colAccess[int(colNumber)]
                    self.show_col_info(field, graphs)
                    stdout.write('`Enter a valid input.`\n')
                colAccess = self.column_menu()
            for field in self.colToDelete:
                self.keep_col(field, False)

        else:
            stdout.write('Columns are going to be automatically processed.')
            for field in self.colToDelete:
                self.keep_col(field, False)

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
            additionalInfo = ''
            if len(catPrint) > 40:
                rand = []
                for i in range(40):
                    rand.append(choice(list(catPrint.keys())))
                catPrint = {k: v for k, v in catPrint.items() if k in rand}

                additionalInfo += 'Too many categories, only displaying a random sample of 40.'

            self.colInfo[col][self.Constants.colLabels] = catPrint

            if self.colInfo[col][self.Constants.colType] is float:
                if len(set([v for v in catDict.values()])) <= 1:
                    self.colToDelete.append(col)
                    additionalInfo += 'Column to be deleted because it contains only one value.'

            elif len(catPrint) <= 1 and col != self.Constants.ID:
                self.colToDelete.append(col)
                additionalInfo += 'Column to be deleted because it contains too many non-numeric categories.'

            self.colInfo[col][self.Constants.colLabelsInfo] = additionalInfo

    def plot_col(self, field):
        """Plot the data of a column."""
        stats.probplot(self.tableColumns[field], dist="norm", plot=pylab)
        pylab.show()

    def rename_col(self, field):
        """Rename columns."""
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

    def keep_col(self, field, boolean):
        """Ask human for decision about the destiny of a column."""
        if boolean is True:
            logging.info('Keeping: %s' % field)
            self.colToDelete = [c for c in self.colToDelete if c != field]
            self.colKept.append(field)

            return True

        else:
            logging.info('Deleting: %s' % field)
            self.colToDelete = [c for c in self.colToDelete if c != field]
            self.tableFields.remove(field)
            self.tableColumns.pop(field)
            self.colInfo.pop(field)
            try:
                for row in self.tableData:
                    row.pop(field)
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
