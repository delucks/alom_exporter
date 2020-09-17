#!/usr/bin/env python
from collections import defaultdict
from typing import List
import json
import sys
import re

# Names from environmental report -> keys in result data / metric name fragments
header_to_category = {
    'System Indicator Status': 'indicator',
    'System Temperatures (Temperatures in Celsius)': 'temperature',
    'Fans (Speeds Revolution Per Minute)': 'fans',
    'Fan Status information': 'fans',
    'Voltage sensors (in Volts)': 'voltage',
    'Voltage Rail Status': 'voltage',
    'System Load (in amps)': 'load',
    'System Load information': 'load',
    'Current sensors': 'current',
    'Current sensor information': 'current',
    'Power Supplies': 'psu',
}

# Non-numeric table values are mapped to floats with this dictionary.
# If your data contains a different value, please file an issue with the output of "showenvironment" and some information about your hardware.
custom_table_values = {
    'OFF': 0.0,
    'OK': 1.0,
    'STANDBY/BLINK': 1.0,
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
        print(f'{header}\t{iterator}\n{data}')
        for idx, hdr in enumerate(header):
            # Skip first column which describes the (sensor/supply ID) key
            if idx == 0:
                continue
            # Use first column as the key for this data
            parsed[data[0]][hdr] = atoi(data[idx])
        iterator += 1
    return parsed, iterator

def parse_system_indicator_status(lines: List[str], start_index: int) -> (dict, int):
    '''Parse a "System Indicator Status" table into a dict mapping indicator IDs to states.
    Return the new index of the iterator along with the resulting data.
    '''
    parsed = {}
    iterator = start_index
    # Column values can be separated by spaces so we need to find the start index of each column
    indexes = []
    header_line = lines[iterator+2]
    for header in header_line.split():
        indexes.append(header_line.index(header))
    values_line = lines[iterator+3] 
    # Manually space and trim each value with the indexes of the headers
    values = [
        values_line[0:indexes[1]].strip(),
        values_line[indexes[1]:indexes[2]].strip(),
        values_line[indexes[2]:].strip(),
    ]
    for idx, hdr in enumerate(header_line.split()):
        parsed[hdr] = values[idx]
    return parsed, iterator+3

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
