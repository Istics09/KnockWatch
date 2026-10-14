import pytest
from core.duration import parse_duration, to_nft

def test_valid():
    assert parse_duration("30d") == 2592000
    assert parse_duration("1mo") == 30 * 86400
    assert parse_duration("1y") == 365 * 86400
    assert parse_duration("15m") == 900
    assert parse_duration(" 2H ") == 7200
    assert parse_duration("35m") == 2100
    assert parse_duration("1w") == 60 * 60 * 24 * 7

def test_perm():
    assert parse_duration("perm") is None

@pytest.mark.parametrize("bad", ["abc", "0d", "10x", "", "5", "-5", "-5d"])
def test_invalid(bad):
    with pytest.raises(ValueError):
        parse_duration(bad)

def test_to_nft():
    assert to_nft(2592000) == "30d"
    assert to_nft(900) == "900s"