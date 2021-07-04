import pytest

from alom.ssh import ALOMConnection


def test_config_parse(tmp_path):
    p = tmp_path / "sample_config.yaml"
    p.write_text("alom_authentication_delay: 2.4\nmax_environment_delay: 10.0\nmin_environment_delay: 0.05\n")
    connection = ALOMConnection(str(p))
    assert connection.config['alom_authentication_delay'] == 2.4
    assert connection.config['max_environment_delay'] == 10.0
    assert connection.config['min_environment_delay'] == 0.05


def test_connection_backoff(tmp_path):
    p = tmp_path / "sample_config.yaml"
    p.write_text("alom_authentication_delay: 2.0\nmax_environment_delay: 10.0\nmin_environment_delay: 0.05\n")
    connection = ALOMConnection(str(p))
    assert connection.backoff == 0.05, "initial state: backoff is not set to min config"
    assert connection.get_backoff() == 0.05
    # increase first time
    connection.increase_backoff()
    assert connection.backoff == 0.1, "backoff was not properly doubled"
    assert connection.get_backoff() == 0.1
    # increase 2nd time
    connection.increase_backoff()
    assert connection.backoff == 0.2, "backoff was not properly doubled"
    assert connection.get_backoff() == 0.2
    # simulate a power-on event
    connection.last_measurement_on = True
    assert connection.backoff == 0.2, "backoff not retained when power cycles on"
    assert connection.get_backoff() == 10.0, "get_backoff did not return max backoff when power is on"
    # simulate a power-off event
    connection.last_measurement_on = False
    assert connection.get_backoff() == 0.2, "get_backoff did not return to the previous backoff when power cycle changed"
