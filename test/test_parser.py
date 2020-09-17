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
    assert result['indicator']['SYS/LOCATE'] == 0
    assert result['indicator']['SYS/SERVICE'] == 0
    assert result['indicator']['SYS/ACT'] == 1
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
    assert result['indicator']['SYS/LOCATE'] == 0
    assert result['indicator']['SYS/SERVICE'] == 0
    assert result['indicator']['SYS/ACT'] == 1
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
    assert result['indicator']['SYS/LOCATE'] == 0
    assert result['indicator']['SYS/SERVICE'] == 0
    assert result['indicator']['SYS/ACT'] == 1
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
