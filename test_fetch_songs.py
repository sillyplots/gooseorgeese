import pytest
from fetch_songs import parse_duration, is_valid_video

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

def test_parse_duration_type_errors():
    """Test inputs of incorrect types, like None or integers."""
    assert parse_duration(None) == 0
    assert parse_duration(123) == 0

def test_parse_duration_malformed_strings():
    """Test duration strings that are malformed or have unexpected components."""
    assert parse_duration("PT10X") == 0
    assert parse_duration("P1D") == 0
    assert parse_duration("PT-5S") == 0

def test_is_valid_video_valid():
    """Test that a valid official video passes."""
    item = {'snippet': {'title': 'Goose - Hungersite (Official Video)'}}
    assert is_valid_video(item, 'Goose') == True

def test_is_valid_video_interview():
    """Test that interviews are rejected."""
    item = {'snippet': {'title': 'Goose Interview with KEXP'}}
    assert is_valid_video(item, 'Goose') == False

def test_is_valid_video_cross_contamination():
    """Test that videos with the other band name are rejected."""
    item = {'snippet': {'title': 'Geese covering Goose'}}
    assert is_valid_video(item, 'Goose') == False

    item2 = {'snippet': {'title': 'Goose playing with Geese'}}
    assert is_valid_video(item2, 'Geese') == False

def test_is_valid_video_cover_without_band_name():
    """Test that covers without the band name in the title are rejected."""
    item = {'snippet': {'title': 'Hungersite - Acoustic Cover'}}
    assert is_valid_video(item, 'Goose') == False

def test_is_valid_video_cover_with_band_name():
    """Test that covers with the band name in the title are accepted."""
    item = {'snippet': {'title': 'Goose - Hungersite - Acoustic Cover'}}
    assert is_valid_video(item, 'Goose') == True

def test_is_valid_video_trailer_teaser_full_album():
    """Test that trailers, teasers, and full albums are rejected."""
    assert is_valid_video({'snippet': {'title': 'Goose - New Album Trailer'}}, 'Goose') == False
    assert is_valid_video({'snippet': {'title': 'Goose - Tour Teaser'}}, 'Goose') == False
    assert is_valid_video({'snippet': {'title': 'Goose - Full Album 2023'}}, 'Goose') == False
