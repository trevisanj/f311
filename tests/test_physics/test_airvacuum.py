from f311 import physics as ph

def test_vacuum_to_air():
    assert ph.vacuum_to_air(1e8/2000) == 49986.36934549974


def test_air_to_vacuum():
    assert 1e8/ph.air_to_vacuum(5500.) == 18176.768046090445
