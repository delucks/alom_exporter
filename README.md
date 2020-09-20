# alom_exporter

This connects to an instance of Sun Advanced Lights-Out Management (ALOM) via SSH and exports metrics about the host system to Prometheus! It has been tested on Sun T1000 and T2000 systems so far- please try it with your system and file a bug if it's not compatible. It is currently focused on `showenvironment` metrics: voltage/amperage/temperature, for safety and environmental monitoring. The system running this exporter requires the following:

- python3
- Network access to the management interface of your target server
- Credentials for logging into the target server in a configuration file, like the following:

```
alom_ssh_address: '192.168.1.231'
alom_ssh_username: admin
alom_ssh_password: changeme
```

Since the `showenvironment` command doesn't require administrative privileges, I'd recommend setting up a dedicated user for alom_exporter to adhere to the principle of least privilege.

## Installation

Install via pip, `pip install alom-exporter` - and note the package name uses a dash. The daemon can be invoked with `alom_exporter`.

## Example

This was generated from example output of a Sun T2000 server. Python metrics are omitted for brevity.

```
# HELP alom_system_temperature Current temperature of system sensors
# TYPE alom_system_temperature gauge
alom_system_temperature{sensor="PDB/T_AMB"} 24.0
alom_system_temperature{sensor="MB/T_AMB"} 28.0
alom_system_temperature{sensor="MB/CMP0/T_TCORE"} 44.0
alom_system_temperature{sensor="MB/CMP0/T_BCORE"} 44.0
alom_system_temperature{sensor="IOBD/IOB/TCORE"} 43.0
alom_system_temperature{sensor="IOBD/T_AMB"} 29.0
# HELP alom_fan_speed Current speed of cooling fans in RPM
# TYPE alom_fan_speed gauge
alom_fan_speed{sensor="FT0/FM0"} 3586.0
alom_fan_speed{sensor="FT0/FM1"} 3525.0
alom_fan_speed{sensor="FT0/FM2"} 3650.0
alom_fan_speed{sensor="FT2"} 2455.0
# HELP alom_voltage_status Current voltage at sensors across the machine
# TYPE alom_voltage_status gauge
alom_voltage_status{sensor="MB/V_+1V5"} 1.48
alom_voltage_status{sensor="MB/V_VMEML"} 1.79
alom_voltage_status{sensor="MB/V_VMEMR"} 1.78
alom_voltage_status{sensor="MB/V_VTTL"} 0.89
alom_voltage_status{sensor="MB/V_VTTR"} 0.89
alom_voltage_status{sensor="MB/V_+3V3STBY"} 3.39
alom_voltage_status{sensor="MB/V_VCORE"} 1.31
alom_voltage_status{sensor="IOBD/V_+1V5"} 1.48
alom_voltage_status{sensor="IOBD/V_+1V8"} 1.79
alom_voltage_status{sensor="IOBD/V_+3V3MAIN"} 3.36
alom_voltage_status{sensor="IOBD/V_+3V3STBY"} 3.41
alom_voltage_status{sensor="IOBD/V_+1V"} 1.11
alom_voltage_status{sensor="IOBD/V_+1V2"} 1.17
alom_voltage_status{sensor="IOBD/V_+5V"} 5.15
alom_voltage_status{sensor="IOBD/V_-12V"} -12.04
alom_voltage_status{sensor="IOBD/V_+12V"} 12.18
alom_voltage_status{sensor="SC/BAT/V_BAT"} 3.06
# HELP alom_system_load Current system load in amps
# TYPE alom_system_load gauge
alom_system_load{sensor="MB/I_VCORE"} 34.64
alom_system_load{sensor="MB/I_VMEML"} 7.56
alom_system_load{sensor="MB/I_VMEMR"} 6.42
# HELP alom_sensor_status Status of current sensors
# TYPE alom_sensor_status gauge
alom_sensor_status{sensor="IOBD/I_USB0"} 1.0
alom_sensor_status{sensor="IOBD/I_USB1"} 1.0
alom_sensor_status{sensor="FIOBD/I_USB"} 1.0
# HELP alom_power_supply_status Status of power supplies
# TYPE alom_power_supply_status gauge
alom_power_supply_status{supply="PS0"} 1.0
alom_power_supply_status{supply="PS1"} 1.0
# HELP alom_ok Scraping status from ALOM
# TYPE alom_ok gauge
alom_ok 1.0
# HELP alom_system_power System power status
# TYPE alom_system_power gauge
alom_system_power 1.0
```
Some examples in this repo's test suite are from this [official Sun documentation](https://docs.oracle.com/cd/E19076-01/t1k.srvr/819-3250-11/command_shell.html).

## License

GPLv3 - a copy is included with this software as `LICENSE.txt`
