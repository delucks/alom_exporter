import time

from prometheus_client import start_http_server, Enum
from prometheus_client.core import GaugeMetricFamily, REGISTRY

from alom.parse import parse_showenvironment
from alom.ssh import ALOMConnection


class ALOMCollector:
    def __init__(self, config_path='config.yaml'):
        self.config_path = config_path

    def collect(self):
        metrics = {}
        metrics['temperature'] = GaugeMetricFamily(
            'alom_system_temperature',
            'Current temperature of system sensors',
            labels=['sensor']
        )
        #metrics['indicator'] = Enum(
        #    'alom_indicator_status',
        #    'Status of each indicator LED',
        #    labelnames=['indicator'],
        #    states=['OFF', 'FAST BLINK', 'STANDBY BLINK']
        #)
        metrics['fans'] = GaugeMetricFamily(
            'alom_fan_speed',
            'Current speed of cooling fans in RPM',
            labels=['sensor']
        )
        metrics['voltage'] = GaugeMetricFamily(
            'alom_voltage_status',
            'Current voltage at sensors across the machine',
            labels=['sensor']
        )
        metrics['load'] = GaugeMetricFamily(
            'alom_system_load',
            'Current system load in amps',
            labels=['sensor']
        )
        metrics['current'] = GaugeMetricFamily(
            'alom_sensor_status',
            'Status of current sensors',
            labels=['sensor']
        )
        metrics['psu'] = GaugeMetricFamily(
            'alom_power_supply_status',
            'Status of power supplies',
            labels=['supply']
        )
        metrics['heartbeat'] = GaugeMetricFamily('alom_ok', 'Scraping status from ALOM')
        metrics['power'] = GaugeMetricFamily('alom_system_power', 'System power status')
        try:
            with open('test/t1000_on_0.txt', 'r') as fh:
                env = fh.read()
            # This is working, but stubbed until I'm confident in the metrics code here
            #with ALOMConnection(self.config_path) as connection:
            #    env = connection.showenvironment()
            trimmed = [line.strip() for line in env.splitlines()]
            data = parse_showenvironment(trimmed)
            metrics['heartbeat'].add_metric([], 1)
        except Exception as e:
            metrics['heartbeat'].add_metric([], 0)
            raise  # Gradually this should become a logging statement so the daemon doesn't crash.
        # Simple metrics
        metrics['power'].add_metric([], data['power']['system'])
        for sensor, sensor_readings in data['temperature'].items():
            # XXX include sensor thresholds (Low/High Hard/Soft/Warn) if appropriate
            metrics['temperature'].add_metric([sensor], sensor_readings['Temp'])
        #for indicator, state in data['indicator'].items():
        #    metrics['indicator'].labels(indicator).state(state)
        for fan_sensor, fan_status in data['fans'].items():
            metrics['fans'].add_metric([fan_sensor], fan_status['Speed'])
        for sensor, sensor_readings in data['voltage'].items():
            metrics['voltage'].add_metric([sensor], sensor_readings['Voltage'])
        for sensor, sensor_readings in data['load'].items():
            metrics['load'].add_metric([sensor], sensor_readings['Load'])
        for sensor, sensor_readings in data['current'].items():
            metrics['current'].add_metric([sensor], sensor_readings['Status'])
        for sensor, sensor_readings in data['psu'].items():
            metrics['psu'].add_metric([sensor], sensor_readings['Status'])
        for metric in metrics.values():
            yield metric

if __name__ == '__main__':
    REGISTRY.register(ALOMCollector())
    start_http_server(9123)
    while True:
        time.sleep(1)
