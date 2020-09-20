#!/usr/bin/env python
from collections import defaultdict
from typing import List
import json
import sys
import re

from alom.exceptions import PartialResponseException

# Names from environmental report -> keys in result data / metric name fragments
header_to_category = {
    'System Indicator Status': 'indicator',
    'System Temperatures (Temperatures in Celsius)': 'temperature',
    'Fans (Speeds Revolution Per Minute)': 'fans',
    'Fans Status': 'fans',
    'Fan Status information': 'fans',
    'Voltage sensors (in Volts)': 'voltage',
    'Voltage Rail Status': 'voltage',
    'System Load (in amps)': 'load',
    'System Load information': 'load',
    'Current sensors': 'current',
    'Current sensor information': 'current',
    'Power Supplies': 'psu',
    'Disk Status information': 'disk',
    'System Disks': 'disk',
}

# Non-numeric table values are mapped to floats with this dictionary.
# If your data contains a different value, please file an issue with the output of "showenvironment" and some information about your hardware.
custom_table_values = {
    'OFF': 0.0,
    'OK': 1.0,
    'NOT PRESENT': -1.0,
    '--': -1.0,
}

def atoi(table_data: str) -> float:
    '''Convert a value from environmental status table into numeric
    representation: a float for float values, 0/1 for binary values'''
    try:
        return float(table_data)
    except ValueError as e:
        if table_data in custom_table_values:
            return custom_table_values[table_data]
        raise Exception(f'Value {table_data} is currently unhandled by the ALOM parser') from e

def parse_table(lines: List[str], start_index: int) -> (dict, int):
    '''Parse a full table from environmental status report, starting with the header.
    Return the table as a nested mapping with the first column (sensor name) as the key for
    each row's values. Also track & return the line count read to avoid double parsing.

    Parameters:
        lines: Full contents of environmental status
        start_index: Index of table header
    '''
    parsed = defaultdict(dict)
    # Find column header line: next line starting with a capital alphanum after start_index
    iterator = start_index+1
    line = lines[iterator]
    while not re.search('^[A-Z]', line):
        iterator += 1
        line = lines[iterator]
    if line == 'Fans (Speeds Revolution Per Minute):':
        # The fans header on T2000 includes an extra line before the table header
        iterator += 1
        line = lines[iterator]
    header = line.split()
    # There is always a divider line after the header, so we can skip that safely
    iterator += 2
    while iterator < len(lines):
        line = lines[iterator]
        if line == "" or line.startswith('----'):
            # This indicates the end of the table- a blank newline or in some cases a final divider
            break
        if 'cannot be displayed when System power is off' in line:
            # Status tables occasionally include some records when power is off.
            # These records are informative only for our purposes so are skipped.
            iterator += 1
            continue
        data = line.split()
        # Using .split() is the most reliable method for most tables, as the headers do not always match up with the values.
        # However, for System Disks, this method results in the token "NOT PRESENT" being broken up.
        for idx, element in enumerate(data):
            if element == 'PRESENT' and data[idx-1] == 'NOT':
                data = data[0:idx-1] + ['NOT PRESENT'] + data[idx+1:]
        #print(f'{header}\t{iterator}\n{data}')
        for idx, hdr in enumerate(header):
            # Skip first column which describes the (sensor/supply ID) key
            if idx == 0:
                continue
            # Use first column as the key for this data
            try:
                parsed[data[0]][hdr] = atoi(data[idx])
            except IndexError as e:
                # partially formed message causes columns to be split
                raise PartialResponseException() from e
        iterator += 1
    return parsed, iterator

def _parse_indicator_row(header_line: str, values_line: str) -> dict:
    result = {}
    # Column values can be separated by spaces so we need to find the start index of each column
    indexes = []
    for header in header_line.split():
        indexes.append(header_line.index(header))
    # Manually space and trim each value with the indexes of the headers
    values = [
        values_line[0:indexes[1]].strip(),
        values_line[indexes[1]:indexes[2]].strip(),
        values_line[indexes[2]:].strip(),
    ]
    for idx, hdr in enumerate(header_line.split()):
        result[hdr] = values[idx]
    return result

def parse_system_indicator_status(lines: List[str], start_index: int) -> (dict, int):
    '''Parse a "System Indicator Status" table into a dict mapping indicator IDs to states.
    Return the new index of the iterator along with the resulting data.
    '''
    iterator = start_index+2  # Skip table header and first divider
    # First table always exists, and in some cases there are additional tables
    result = _parse_indicator_row(lines[iterator], lines[iterator+1])
    iterator += 2  # Skip first table
    while iterator < len(lines):
        # An empty line means we've hit the end of this table
        if lines[iterator] == '' or lines[iterator+1] == '':
            break
        # A divider followed by a capital letter in first position means we've found another row
        if lines[iterator].startswith('----') and re.search('^[A-Z]', lines[iterator+1]):
            iterator += 1
            # Merge in additional rows
            next_row = _parse_indicator_row(lines[iterator], lines[iterator+1])
            for k, v in next_row.items():
                result[k] = v
            iterator += 2  # Skip this table
    return result, iterator

def parse_showenvironment(lines: List[str]) -> dict:
    result = defaultdict(dict)
    result['power']['system'] = 1  # Assume power on until we hit a "System power is off" line

    iterator = 0
    while iterator < len(lines):
        line = lines[iterator]
        if re.search(':$', line):
            header = line.rstrip(':')
            #print(f'Header: {header}')
            # Special case- several boolean columns with no divider
            if header == 'System Indicator Status':
                indicators, new_index = parse_system_indicator_status(lines, iterator)
                result['indicator'] = indicators
                iterator = new_index
                continue
            # The rest are all proper tables
            table, new_index = parse_table(lines, iterator)
            result[header_to_category[header]] = table
            result['power'][header_to_category[header]] = 1
            iterator = new_index  # This is the end of the table and should still be incremented below
        elif 'cannot be displayed when System power is off' in line:
            result['power']['system'] = 0
            header = ' '.join(line.split()[:3])
            result['power'][header_to_category[header]] = 0
        iterator += 1

    #print(json.dumps(result, indent=2))
    return result
