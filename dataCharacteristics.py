"""Preformat data before  Machine Learning algorithms."""

# TODO add a file parser to choose file input

import logging
from os import getcwd
import csv
import sys
from dataStatistics import route_cols


__author__ = 'Etienne Pouget'

logging.basicConfig(
    level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

logging.info('dataCharacteristics Started')


def assert_data_format(data):
    """Make sure the input data is correctly formatted.

    Return only correctly formatted rows.
    """
    counter = {'normal': 0, 'malformatted': 0, 'total': 0}
    dataOutput = []
    try:
        assert isinstance(data, list), 'Input must be a list'
    except AssertionError as e:
        logging.critical('Incorrect input')
        raise AssertionError(e)
    for row in data:
        try:
            assert isinstance(row, dict), 'Rows must be dictionaries'
            counter['normal'] += 1
            dataOutput.append(row)
        except AssertionError as e:
            logging.warning('Malformatted item: {}\n{}'.format(row, e))
            counter['malformatted'] += 1

    counter['total'] = counter['malformatted'] + counter['normal']
    cntrStr = {k: str(v) for k, v in counter.items()}

    logging.debug(
        "Dataset contains {} rows, {} are malformatted, {} are normal".format(
         cntrStr['total'], cntrStr['malformatted'], cntrStr['normal']))

    return dataOutput, counter


def dataDimensions(data):
    """"Print the dimensions of the dataset."""
    logging.info('Number of rows of data: %s' % len(data))
    logging.info('Number of columns of data: %s' % len(data[1]))


def csvToDict(filepath):
    """Convert a csv to a list of dictionaries."""
    data = []
    with open(getcwd() + filepath, 'r') as dataset:
        assert csv.Sniffer().has_header(dataset.read(9999)), 'No headers'
        dataset.seek(0)
        dialect = csv.Sniffer().sniff(dataset.read(99999))
        dataset.seek(0)
        reader = csv.DictReader(dataset, dialect=dialect)
        headers = reader.fieldnames
        for row in reader:
            data.append(row)

    data = assert_data_format(data)[0]

    return data, headers


def find_data_type(data, headers):
    """Produce columns statistics on the type of data they contains."""
    colCounts = []
    for h in headers:
        dType = [0]*3
        for row in data:
            try:
                a = float(row[h])
                if isinstance(a, float):
                    dType[0] += 1
            except ValueError:
                if len(row[h]) > 1:
                    dType[1] += 1
                else:
                    dType[2] += 1
        colCounts.append(dType)

    sys.stdout.write('{:2}-{:20}  {:10}  {:10}  {:10}\n'.format(
        '#', 'Col#', 'Number', 'Strings', 'Other'))

    iCol = 0
    for types in colCounts:
        sys.stdout.write('{:2}-{:20}  {:10}  {:10}  {:10}\n'.format(
            iCol, headers[iCol][:19], types[0], types[1], types[2]))
        iCol += 1

if __name__ == '__main__':
    # filepath = input('Enter filepath from script directory \
    #                 (/example/data.csv):   ')
    filepath = '/us-data-veggies/clean-us-veggies-exp.csv'
    data, headers = csvToDict(filepath)
    dataDimensions(data)
    find_data_type(data, headers)
    data, fieldnames = route_cols(data, headers)

    with open(getcwd() + '/us-data-veggies/work-us-veggies-exp.csv', 'w') as f:
        writer = csv.DictWriter(f, fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
