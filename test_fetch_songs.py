import pytest
import json
from unittest.mock import patch, MagicMock, mock_open
from fetch_songs import parse_duration, get_video_details, search_youtube_page, main, BANDS

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

@patch('urllib.request.urlopen')
def test_get_video_details_success(mock_urlopen):
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "items": [
            {
                "id": "vid1",
                "contentDetails": {"duration": "PT4M13S"}
            },
            {
                "id": "vid2",
                "contentDetails": {"duration": "PT1H"}
            }
        ]
    }).encode('utf-8')
    mock_response.__enter__.return_value = mock_response
    mock_urlopen.return_value = mock_response

    result = get_video_details(["vid1", "vid2"], "test_key")
    assert result == {"vid1": 253, "vid2": 3600}
    mock_urlopen.assert_called_once_with(
        "https://www.googleapis.com/youtube/v3/videos?part=contentDetails&id=vid1,vid2&key=test_key"
    )

def test_get_video_details_empty():
    assert get_video_details([], "test_key") == {}

@patch('urllib.request.urlopen')
def test_get_video_details_error(mock_urlopen):
    mock_urlopen.side_effect = Exception("API Error")
    result = get_video_details(["vid1"], "test_key")
    assert result == {}

@patch('urllib.request.urlopen')
def test_search_youtube_page_success(mock_urlopen):
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "items": [
            {"id": {"videoId": "vid1"}},
            {"id": {"videoId": "vid2"}}
        ]
    }).encode('utf-8')
    mock_response.__enter__.return_value = mock_response
    mock_urlopen.return_value = mock_response

    result = search_youtube_page("test query", "test_key", channel_id="channel_1", page_token="page_1")
    assert "items" in result
    assert len(result["items"]) == 2
    mock_urlopen.assert_called_once_with(
        "https://www.googleapis.com/youtube/v3/search?part=snippet&q=test%20query&type=video&maxResults=50&key=test_key&channelId=channel_1&pageToken=page_1"
    )

@patch('urllib.request.urlopen')
def test_search_youtube_page_no_channel_or_page(mock_urlopen):
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({"items": []}).encode('utf-8')
    mock_response.__enter__.return_value = mock_response
    mock_urlopen.return_value = mock_response

    result = search_youtube_page("test query", "test_key")
    assert "items" in result
    mock_urlopen.assert_called_once_with(
        "https://www.googleapis.com/youtube/v3/search?part=snippet&q=test%20query&type=video&maxResults=50&key=test_key"
    )

@patch('urllib.request.urlopen')
def test_search_youtube_page_error(mock_urlopen):
    mock_urlopen.side_effect = Exception("API Error")
    result = search_youtube_page("test query", "test_key")
    assert result == {}

@patch('fetch_songs.search_youtube_page')
@patch('fetch_songs.get_video_details')
@patch('builtins.open', new_callable=mock_open)
def test_main_success_flow_and_filtering(mock_open, mock_get_video_details, mock_search_youtube_page):
    # Mocking search_youtube_page to return a set of items for Goose, then none for Geese
    def side_effect_search(query, api_key, channel_id=None, page_token=None):
        if 'Goose' in query:
            return {
                "items": [
                    {"id": {"videoId": "vid1"}, "snippet": {"title": "Goose - A good song"}},
                    {"id": {"videoId": "vid2"}, "snippet": {"title": "Goose interview"}}, # Filtered: interview
                    {"id": {"videoId": "vid3"}, "snippet": {"title": "Geese crossover"}}, # Filtered: other band
                    {"id": {"videoId": "vid4"}, "snippet": {"title": "Random cover"}}, # Filtered: cover but not by band
                    {"id": {"videoId": "vid5"}, "snippet": {"title": "Goose cover of a song"}}, # Kept: cover but band is in title
                    {"id": {"videoId": "vid6"}, "snippet": {"title": "Goose - Short song"}} # Kept: but duration will be short
                ]
            }
        elif 'Geese' in query:
            return {"items": []} # No items for Geese to keep test simple
        return {"items": []}

    mock_search_youtube_page.side_effect = side_effect_search

    # Mocking get_video_details to return durations
    mock_get_video_details.return_value = {
        "vid1": 300, # Good duration
        "vid5": 400, # Good duration
        "vid6": 20   # Too short (< 30s), will be filtered
    }

    # Patch json.dump to easily inspect the data being written
    with patch('json.dump') as mock_json_dump:
        main()

        # Assert get_video_details was called with correct filtered video ids
        mock_get_video_details.assert_called_once()
        args, kwargs = mock_get_video_details.call_args
        video_ids = args[0]
        assert set(video_ids) == {"vid1", "vid5", "vid6"}

        mock_open.assert_called_with('new_songs.json', 'w')

        # Verify the saved songs
        mock_json_dump.assert_called_once()
        saved_data = mock_json_dump.call_args[0][0]

        assert len(saved_data) == 2 # vid1 and vid5 (vid6 filtered by length)
        assert saved_data[0]['youtubeId'] == 'vid1'
        assert saved_data[0]['artist'] == 'Goose'
        assert saved_data[0]['duration'] == 15
        assert saved_data[1]['youtubeId'] == 'vid5'
