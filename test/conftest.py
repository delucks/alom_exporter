import pytest

@pytest.fixture
def sample_session():
    def _sample_session(path):
        with open(path, 'r') as fh:
            return [line.strip() for line in fh.read().splitlines()]
    return _sample_session
