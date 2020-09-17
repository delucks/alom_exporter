import pytest

from alom.parse import parse_showenvironment, atoi


def test_atoi():
    assert atoi('OK') == 1.0
    assert atoi('OFF') == 0.0
    assert atoi('8923') == 8923
    assert atoi('-1') == -1
    assert atoi('213.1280') == 213.1280

def test_t1000_on_0(sample_session):
    test = sample_session('test/t1000_on_0.txt')
    result = parse_showenvironment(test)
    # Temperature block
    assert result['power']['temperature'] == 1
    assert result['temperature']['MB/T_AMB']['Status'] == 1
    assert result['temperature']['MB/T_AMB']['Temp'] == 25
    assert result['temperature']['MB/CMP0/T_TCORE']['Temp'] == 37
    assert result['temperature']['MB/CMP0/T_BCORE']['Temp'] == 37
    assert result['temperature']['MB/IOB/T_CORE']['Temp'] == 37
    # Indicators
    assert result['indicator']['SYS/LOCATE'] == 'OFF'
    assert result['indicator']['SYS/SERVICE'] == 'OFF'
    assert result['indicator']['SYS/ACT'] == 'ON'
    # Fans
    assert result['power']['fans'] == 1
    assert result['fans']['FT0/F0']['Speed'] == 8967
    assert result['fans']['FT0/F1']['Speed'] == 8776
    assert result['fans']['FT0/F2']['Speed'] == 9166
    assert result['fans']['FT0/F3']['Speed'] == 8776
    # Voltage
    assert result['power']['voltage'] == 1
    assert result['voltage']['MB/V_VCORE']['Voltage'] == 1.30
    assert result['voltage']['MB/V_VMEM']['Voltage'] == 1.79
    assert result['voltage']['MB/V_VTT']['Voltage'] == 0.89
    assert result['voltage']['MB/V_+1V2']['Voltage'] == 1.18
    assert result['voltage']['MB/V_+1V5']['Voltage'] == 1.48
    assert result['voltage']['MB/V_+2V5']['Voltage'] == 2.50
    assert result['voltage']['MB/V_+3V3']['Voltage'] == 3.31
    assert result['voltage']['MB/V_+5V']['Voltage'] == 5.02
    assert result['voltage']['MB/V_+12V']['Voltage'] == 12.25
    assert result['voltage']['MB/V_+3V3STBY']['Voltage'] == 3.38
    # Load
    assert result['power']['load'] == 1
    assert result['load']['MB/I_VCORE']['Load'] == 11.2
    assert result['load']['MB/I_VMEM']['Load'] == 2.88
    # Current
    assert result['current']['MB/BAT/V_BAT']['Status'] == 1
    # Power supplies
    assert result['psu']['PS0']['Status'] == 1

def test_t1000_on_1(sample_session):
    test = sample_session('test/t1000_on_1.txt')
    result = parse_showenvironment(test)
    # Temperature block
    assert result['power']['temperature'] == 1
    assert result['temperature']['MB/T_AMB']['Status'] == 1
    assert result['temperature']['MB/T_AMB']['Temp'] == 25
    assert result['temperature']['MB/CMP0/T_TCORE']['Temp'] == 38
    assert result['temperature']['MB/CMP0/T_BCORE']['Temp'] == 38
    assert result['temperature']['MB/IOB/T_CORE']['Temp'] == 37
    # Indicators
    assert result['indicator']['SYS/LOCATE'] == 'OFF'
    assert result['indicator']['SYS/SERVICE'] == 'OFF'
    assert result['indicator']['SYS/ACT'] == 'ON'
    # Fans
    assert result['power']['fans'] == 1
    assert result['fans']['FT0/F0']['Speed'] == 8967
    assert result['fans']['FT0/F1']['Speed'] == 8776
    assert result['fans']['FT0/F2']['Speed'] == 8967
    assert result['fans']['FT0/F3']['Speed'] == 8776
    # Voltage
    assert result['power']['voltage'] == 1
    assert result['voltage']['MB/V_VCORE']['Voltage'] == 1.31
    assert result['voltage']['MB/V_VMEM']['Voltage'] == 1.79
    assert result['voltage']['MB/V_VTT']['Voltage'] == 0.89
    assert result['voltage']['MB/V_+1V2']['Voltage'] == 1.19
    assert result['voltage']['MB/V_+1V5']['Voltage'] == 1.48
    assert result['voltage']['MB/V_+2V5']['Voltage'] == 2.49
    assert result['voltage']['MB/V_+3V3']['Voltage'] == 3.29
    assert result['voltage']['MB/V_+5V']['Voltage'] == 5.02
    assert result['voltage']['MB/V_+12V']['Voltage'] == 12.25
    assert result['voltage']['MB/V_+3V3STBY']['Voltage'] == 3.38
    # Load
    assert result['power']['load'] == 1
    assert result['load']['MB/I_VCORE']['Load'] == 11.2
    assert result['load']['MB/I_VMEM']['Load'] == 2.88
    # Current
    assert result['current']['MB/BAT/V_BAT']['Status'] == 1
    # Power supplies
    assert result['psu']['PS0']['Status'] == 1

def test_t1000_on_docs_example(sample_session):
    test = sample_session('test/t1000_on_docs_example.txt')
    result = parse_showenvironment(test)
    # Temperature block
    assert result['power']['temperature'] == 1
    assert result['temperature']['MB/T_AMB']['Status'] == 1
    assert result['temperature']['MB/T_AMB']['Temp'] == 26
    assert result['temperature']['MB/CMP0/T_TCORE']['Temp'] == 42
    assert result['temperature']['MB/CMP0/T_BCORE']['Temp'] == 42
    assert result['temperature']['MB/IOB/T_CORE']['Temp'] == 36
    # Indicators
    assert result['indicator']['SYS/LOCATE'] == 'OFF'
    assert result['indicator']['SYS/SERVICE'] == 'OFF'
    assert result['indicator']['SYS/ACT'] == 'ON'
    # Fans
    assert result['power']['fans'] == 1
    assert result['fans']['FT0/F0']['Speed'] == 6653
    assert result['fans']['FT0/F1']['Speed'] == 6653
    assert result['fans']['FT0/F2']['Speed'] == 6653
    assert result['fans']['FT0/F3']['Speed'] == 6547
    # Voltage
    assert result['power']['voltage'] == 1
    assert result['voltage']['MB/V_VCORE']['Voltage'] == 1.31
    assert result['voltage']['MB/V_VMEM']['Voltage'] == 1.78
    assert result['voltage']['MB/V_VTT']['Voltage'] == 0.89
    assert result['voltage']['MB/V_+1V2']['Voltage'] == 1.19
    assert result['voltage']['MB/V_+1V5']['Voltage'] == 1.49
    assert result['voltage']['MB/V_+2V5']['Voltage'] == 2.50
    assert result['voltage']['MB/V_+3V3']['Voltage'] == 3.29
    assert result['voltage']['MB/V_+5V']['Voltage'] == 5.02
    assert result['voltage']['MB/V_+12V']['Voltage'] == 12.18
    assert result['voltage']['MB/V_+3V3STBY']['Voltage'] == 3.31
    # Load
    assert result['power']['load'] == 1
    assert result['load']['MB/I_VCORE']['Load'] == 21.52
    assert result['load']['MB/I_VMEM']['Load'] == 1.74
    # Current
    assert result['current']['MB/BAT/V_BAT']['Status'] == 1
    # Power supplies
    assert result['psu']['PS0']['Status'] == 1

def test_t1000_off(sample_session):
    test = sample_session('test/t1000_off.txt')
    result = parse_showenvironment(test)
    # Temperature block
    assert result['power']['temperature'] == 1
    assert result['temperature']['MB/T_AMB']['Status'] == 1
    assert result['temperature']['MB/T_AMB']['Temp'] == 25
    # Indicators
    assert result['indicator']['SYS/LOCATE'] == 'FAST BLINK'
    assert result['indicator']['SYS/SERVICE'] == 'OFF'
    assert result['indicator']['SYS/ACT'] == 'STANDBY BLINK'
    # Fans
    assert result['power']['fans'] == 0
    # Voltage
    assert result['power']['voltage'] == 0
    # Load
    assert result['power']['load'] == 0
    # Current
    assert result['power']['current'] == 0
    # Power supplies
    assert result['psu']['PS0']['Status'] == 1

def test_t2000_off(sample_session):
    test = sample_session('test/t2000_off_docs_example.txt')
    result = parse_showenvironment(test)
    # Temperature block
    assert result['power']['temperature'] == 1
    assert result['temperature']['PDB/T_AMB']['Status'] == 1
    assert result['temperature']['PDB/T_AMB']['Temp'] == 24
    # Indicators
    assert result['indicator']['SYS/LOCATE'] == 'OFF'
    assert result['indicator']['SYS/SERVICE'] == 'OFF'
    assert result['indicator']['SYS/ACT'] == 'STANDBY BLINK'
    assert result['indicator']['SYS/REAR_FAULT'] == 'OFF'
    assert result['indicator']['SYS/TEMP_FAULT'] == 'OFF'
    assert result['indicator']['SYS/TOP_FAN_FAULT'] == 'OFF'
    # Disk
    assert result['power']['disk'] == 0
    # Fans
    assert result['power']['fans'] == 0
    # Voltage
    assert result['power']['voltage'] == 0
    # Load
    assert result['power']['load'] == 0
    # Current
    assert result['power']['current'] == 0
    # Power supplies
    assert result['psu']['PS0']['Status'] == 1
    assert result['psu']['PS1']['Status'] == 1

def test_t2000_on(sample_session):
    test = sample_session('test/t2000_on_docs_example.txt')
    result = parse_showenvironment(test)
    # Temperature block
    assert result['power']['temperature'] == 1
    assert result['temperature']['PDB/T_AMB']['Status'] == 1
    assert result['temperature']['PDB/T_AMB']['Temp'] == 24
    assert result['temperature']['MB/T_AMB']['Temp'] == 28
    assert result['temperature']['MB/CMP0/T_TCORE']['Temp'] == 44
    assert result['temperature']['MB/CMP0/T_BCORE']['Temp'] == 44
    assert result['temperature']['IOBD/IOB/TCORE']['Temp'] == 43
    assert result['temperature']['IOBD/T_AMB']['Temp'] == 29
    # Indicators
    assert result['indicator']['SYS/LOCATE'] == 'OFF'
    assert result['indicator']['SYS/SERVICE'] == 'OFF'
    assert result['indicator']['SYS/ACT'] == 'ON'
    assert result['indicator']['SYS/REAR_FAULT'] == 'OFF'
    assert result['indicator']['SYS/TEMP_FAULT'] == 'OFF'
    assert result['indicator']['SYS/TOP_FAN_FAULT'] == 'OFF'
    # Disk
    assert result['power']['disk'] == 1
    assert result['disk']['HDD0']['Status'] == 1.0
    assert result['disk']['HDD1']['Status'] == -1.0
    assert result['disk']['HDD2']['Status'] == -1.0
    assert result['disk']['HDD3']['Status'] == -1.0
    # Fans
    assert result['power']['fans'] == 1
    assert result['fans']['FT0/FM0']['Speed'] == 3586
    assert result['fans']['FT0/FM1']['Speed'] == 3525
    assert result['fans']['FT0/FM2']['Speed'] == 3650
    assert result['fans']['FT2']['Speed'] == 2455
    # Voltage
    assert result['power']['voltage'] == 1
    assert result['voltage']['MB/V_+1V5']['Voltage'] == 1.48
    assert result['voltage']['MB/V_VMEML']['Voltage'] == 1.79
    assert result['voltage']['MB/V_VMEMR']['Voltage'] == 1.78
    assert result['voltage']['MB/V_VTTL']['Voltage'] == 0.89
    assert result['voltage']['MB/V_VTTR']['Voltage'] == 0.89
    assert result['voltage']['MB/V_+3V3STBY']['Voltage'] == 3.39
    assert result['voltage']['MB/V_VCORE']['Voltage'] == 1.31
    assert result['voltage']['IOBD/V_+1V5']['Voltage'] == 1.48
    assert result['voltage']['IOBD/V_+1V8']['Voltage'] == 1.79
    assert result['voltage']['IOBD/V_+3V3MAIN']['Voltage'] == 3.36
    assert result['voltage']['IOBD/V_+3V3STBY']['Voltage'] == 3.41
    assert result['voltage']['IOBD/V_+1V']['Voltage'] == 1.11
    assert result['voltage']['IOBD/V_+1V2']['Voltage'] == 1.17
    assert result['voltage']['IOBD/V_+5V']['Voltage'] == 5.15
    assert result['voltage']['IOBD/V_-12V']['Voltage'] == -12.04
    assert result['voltage']['IOBD/V_+12V']['Voltage'] == 12.18
    assert result['voltage']['SC/BAT/V_BAT']['Voltage'] == 3.06
    # Load
    assert result['power']['load'] == 1
    assert result['load']['MB/I_VCORE']['Load'] == 34.64
    assert result['load']['MB/I_VMEML']['Load'] == 7.56
    assert result['load']['MB/I_VMEMR']['Load'] == 6.42
    # Current
    assert result['power']['current'] == 1
    assert result['current']['IOBD/I_USB0']['Status'] == 1
    assert result['current']['IOBD/I_USB1']['Status'] == 1
    assert result['current']['FIOBD/I_USB']['Status'] == 1
    # Power supplies
    assert result['psu']['PS0']['Status'] == 1
    assert result['psu']['PS1']['Status'] == 1
