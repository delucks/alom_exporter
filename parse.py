#!/usr/bin/env python
from collections import defaultdict
from typing import List
import json
import sys
import re

def atoi(table_data: str) -> float:
    '''Convert a value from environmental status table into numeric
    representation: a float for float values, 0/1 for binary values'''
    try:
        return float(table_data)
    except ValueError:
        # TODO include other error states here
        if table_data == 'OFF':
            return 0.0
        else:
            return 1.0

def parse_table(lines: List[str], start_index: int) -> (dict, int):
    '''Parse a full table from environmental status report, starting with the header.
    Return the table as a nested mapping with the first column (sensor name) as the key for
    each row's values. Also track & return the line count read to avoid double parsing.
    '''
    header = lines[start_index].split()
    parsed = defaultdict(dict)
    iterator = start_index+2  # Skip --- header line
    line = lines[iterator]
    while line != "" and not line.startswith('---'):  # End of a status table is a bare newline
        # Status tables occasionally include some records when power is off
        if 'cannot be displayed when System power is off' in line:
            iterator += 1
            line = lines[iterator]
            continue
        data = line.split()
        #print(header, data, line)
        for idx, hdr in enumerate(header):
            # Skip first column which describes the (sensor/supply ID) key
            if idx == 0:
                continue
            # Use first column as the key for this data
            parsed[data[0]][hdr] = atoi(data[idx])
        iterator += 1
        line = lines[iterator]
    return parsed, iterator

'''
ilom_system_temperature = gauge "Current temperature of system sensors"
{
    sensor="MB/T_AMB"
    status="OK"
}
ilom_indicator_status = bool "Whether each indicator LED is lit"
{
    indicator="SYS/LOCATE"
}
ilom_fan_speed = gauge "Current speed of cooling fans"
{
    sensor="FT0/F0"
    status="OK"
}
ilom_voltage_status = gauge "Current voltage measured across the motherboard"
{
    sensor="MB/V_+12V"
    status="OK"
}
ilom_system_load = gauge "Current system load in amps"
{
    sensor="MB/I_VCORE"
    status="OK"
}
ilom_sensor_status = bool "Status of sensors"
{
    sensor="MB/BAT/V_BAT"
}
ilom_power_supply_status = bool "Status of power supplies"
{
    supply="PS0"
}
'''

with open(sys.argv[1]) as f:
    lines = f.read().splitlines()

result = defaultdict(dict)
result['power']['system'] = 1  # Assume power on until we hit a "System power is off" line

iterator = 0
while iterator < len(lines):
    line = lines[iterator]
    if re.match('=* Environmental Status =*', line):
        ...
    elif re.search(':$', line):
        header = line.rstrip(':')
        print(f'Header: {header}')
        # Special case- several boolean columns with no divider
        if header == 'System Indicator Status':
            col_headers = lines[iterator+2].split()
            col_values = lines[iterator+3].split()
            for idx, hdr in enumerate(col_headers):
                result['indicator'][hdr] = 0 if col_values[idx] == 'OFF' else 1
            iterator += 3 # skip the table body
            continue
        # The rest are all proper tables
        table, new_index = parse_table(lines, iterator+2)
        if header == 'System Temperatures (Temperatures in Celsius)':
            result['temperature'] = table
        elif header == 'Fans (Speeds Revolution Per Minute)':
            result['fans'] = table
        elif header == 'Voltage sensors (in Volts)':
            result['voltage'] = table
        elif header == 'System Load (in amps)':
            result['load'] = table
        elif header == 'Current sensors':
            result['current'] = table
        elif header == 'Power Supplies':
            result['psu'] = table
        iterator = new_index
    elif 'cannot be displayed when System power is off' in line:
        result['power']['system'] = 0
        #print('Power off status for ' + ' '.join(line.split()[:3]))

    iterator += 1

print(json.dumps(result, indent=2))
