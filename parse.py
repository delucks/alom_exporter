#!/usr/bin/env python
from typing import List
import json
import sys
import re

def parse_table(lines: List[str], start_index: int) -> (dict, int):
    header = lines[start_index].split()
    parsed = {}
    iterator = start_index+2  # Skip --- header line
    line = lines[iterator]
    while line != "" and not line.startswith('---'):  # End of a status table is a bare newline
        data = line.split()
        print(header, data, line)
        for idx, hdr in enumerate(header):
            parsed[hdr] = data[idx]
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

indicator_status = {}

iterator = 0
while iterator < len(lines):
    line = lines[iterator]
    if re.match('=* Environmental Status =*', line):
        print('Starting status block')
    elif re.search(':$', line):
        header = line.rstrip(':')
        if header == "System Indicator Status":
            # Special case- several boolean columns with no divider
            col_headers = lines[iterator+2].split()
            col_values = lines[iterator+3].split()
            for idx, hdr in enumerate(col_headers):
                indicator_status[hdr] = col_values[idx]
            iterator += 3 # skip the table body
            continue
        print(f'Header: {header}')
        table, new_index = parse_table(lines, iterator+2)
        print(table)
        iterator = new_index
    elif 'cannot be displayed when System power is off' in line:
        print('Power off status for ' + ' '.join(line.split()[:3]))

    iterator += 1

print(json.dumps(indicator_status, indent=2))
