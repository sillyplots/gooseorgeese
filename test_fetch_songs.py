import pytest
from fetch_songs import parse_duration

def test_parse_duration_full():
    """Test full ISO 8601 duration string with hours, minutes, and seconds."""
    assert parse_duration("PT1H2M3S") == 3723
    assert parse_duration("PT10H5M20S") == 36320

def test_parse_duration_missing_components():
    """Test duration strings with missing components."""
    assert parse_duration("PT4M13S") == 253
    assert parse_duration("PT30S") == 30
    assert parse_duration("PT5M") == 300
    assert parse_duration("PT1H") == 3600
    assert parse_duration("PT1H30S") == 3630

def test_parse_duration_empty_or_zero():
    """Test empty, zero, or barely-present components."""
    assert parse_duration("PT") == 0
    assert parse_duration("PT0S") == 0
    assert parse_duration("PT0H0M0S") == 0

def test_parse_duration_large_numbers():
    """Test with numbers that exceed normal time boundaries (e.g. 90 minutes)."""
    assert parse_duration("PT90M") == 5400
    assert parse_duration("PT120S") == 120

def test_parse_duration_invalid_strings():
    """Test invalid or non-matching strings."""
    assert parse_duration("invalid") == 0
    assert parse_duration("") == 0
    # Function is currently case-sensitive so this should fail to match and return 0
    assert parse_duration("pt4m13s") == 0
    assert parse_duration("1H2M3S") == 0 # missing PT prefix
