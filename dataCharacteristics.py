"""Preformat data before  Machine Learning algorithms."""

# TODO add a file parser to choose file input

import logging
from os import getcwd
import csv
from dataStatistics import TableData


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


if __name__ == '__main__':
    # filepath = input('Enter filepath from script directory \
    #                 (/example/data.csv):   ')
    filepath = '/us-data-veggies/clean-us-veggies-exp.csv'
    data, headers = csvToDict(filepath)
    dataDimensions(data)
    table = TableData('veggies', data, headers)
    table.start_analysis()

    with open(getcwd() + '/us-data-veggies/work-us-veggies-exp.csv', 'w') as f:
        writer = csv.DictWriter(f, table.tableFields)
        writer.writeheader()
        for row in table.tableData:
            writer.writerow(row)
