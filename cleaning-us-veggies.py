"""Clean US veggie records."""

import csv
import re
from os import getcwd
import pprint
import logging

logging.basicConfig(
    level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')


# TODO: eliminate the records without month, eliminate empty columns


def csv_to_dict(filename):
    """Convert a csv to a list of dictionaries."""
    nPattern = re.compile("(?<=Commodity:\s)(.+)(?=\s\()")
    yPattern = "(?<!.)(\d{4})(?!.)"
    mPattern = "(?<!.)(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(?!.)"
    mSubstitution = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                     'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                     'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12',
                     None: None}
    cleanDict = {}

    with open(getcwd() + filename, 'r') as datafile:
        dialect = guess_dialect(datafile)
        reader = csv.DictReader(datafile, dialect=dialect)
        headers = reader.fieldnames.copy()
        headers.insert(0, 'month')
        headers.insert(0, 'year')
        headers.insert(0, 'name')
        headers.insert(0, 'id')

        for row in reader:
            try:
                name = nPattern.search(row['Textbox9']).groups()[0]
            except AttributeError:
                print(row['Textbox9'])
                print(nPattern.search(row['Textbox9']))
            year = find_pattern(row, yPattern)
            row = clean_dict(row, year)
            month = find_pattern(row, mPattern)
            row = clean_dict(row, month)
            month = mSubstitution[month]
            rowID = name + '-' + str(year) + '-' + str(month)
            row['id'] = rowID
            row["year"] = year
            row["month"] = month
            row["name"] = name
            row = {k: v for k, v in row.items() if v}
            cleanDict.setdefault(rowID, {})
            for r in row:
                if r not in cleanDict[rowID].keys():
                    cleanDict[rowID][r] = row[r]

    data = [v for v in cleanDict.values()]

    return dialect, headers, data


def dict_to_csv(filename, dialect, headers, data):
    """Write the results into a new file."""
    with open(getcwd() + filename, 'w') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=headers, dialect=dialect)
        writer.writeheader()
        for row in data:
            assert isinstance(row, dict), 'data rows must be dictionaries.'
            writer.writerow(row)


def guess_dialect(datafile, lenToHeaders=9999, lenToDialect=99999):
    """Guess the dialect of a csv file."""
    assert csv.Sniffer().has_header(datafile.read(lenToHeaders)), 'No headers'
    datafile.seek(0)
    dialect = csv.Sniffer().sniff(datafile.read(lenToDialect))
    datafile.seek(0)

    return dialect


def find_pattern(dictionary, pattern):
    """Find a pattern in a dictionary."""
    pattern = re.compile(pattern)
    results = []
    for v in dictionary.values():
        if pattern.search(v):
            results.extend(pattern.match(v).groups())

    results = list(set(results))
    try:
        results = [int(r) for r in results if int(r) > 1990 and int(r) < 2030]
    except ValueError:
        pass

    cntr = 0
    if len(results) > 1:
        for k, v in dictionary.items():
            for r in results:
                try:
                    if int(v) == r:
                        if 'year' in k:
                            return r
                except ValueError:
                    pass

    elif len(results) > 1:
        for r in results:
            print(str(cntr) + " - " + str(r))
            cntr += 1
        while True:
            resultsIndex = input("which is the correct input?   ")
            try:
                resultsIndex = int(resultsIndex)
                break
            except ValueError:
                print('Invalid input')
        print(str(results[resultsIndex]))
        return str(results[resultsIndex])

    else:
        try:
            return str(results[0])
        except IndexError:
            return None


def clean_dict(dictionary, value):
    """Clean a dictionary of all the keys having a specific value."""
    assert isinstance(dictionary, dict)
    delKeys = []
    for k, v in dictionary.items():
        if v == value:
            delKeys.append(k)

    for k in delKeys:
        dictionary.pop(k)

    return dictionary


def clean_empty_columns(data, threshold=0):
    """Delete columns if less than the threshold of valid data."""
    columns = {}
    cleanList = []
    errorList = []
    for row in data:
        for k, v in row.items():
            columns.setdefault(k, 0)
            try:
                if row['month']:
                    if v:
                        columns[k] += 1
            except KeyError:
                errorList.append(row)

    columnStats = {k: '{:.2%}'.format(v/len(data)) for k, v in columns.items()}
    logging.info(pprint.pformat(columnStats, indent=4))

    delColumns = []
    for k, v in columns.items():
        if v / len(data) <= threshold:
            logging.info('Deleting "%s" column' % k)
            delColumns.append(k)

    for row in data:
        for k in delColumns:
            try:
                row.pop(k)
                columns.pop(k)
            except KeyError:
                pass
        try:
            if row['month']:
                cleanList.append(row)
        except KeyError:
            pass

    return cleanList, errorList, [k for k in columns.keys()]


if __name__ == '__main__':
    filename = '/us-data-veggies/us-veggies-exp.csv'
    dialect, headers, data = csv_to_dict(filename)
    data, errorList, updated_headers = clean_empty_columns(data)
    headers = [i for i in headers if i in updated_headers]
    print(len(headers))
    print(len(updated_headers))

    filename = '/us-data-veggies/clean-us-veggies-exp.csv'
    dict_to_csv(filename=filename, dialect=dialect, headers=headers, data=data)
