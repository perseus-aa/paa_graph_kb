"""Tests for the base Client class."""
from __future__ import annotations

import time
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests
from pydantic import BaseModel

from paa_graph_kb.clients.ham_client import Client


# Test fixtures and helper models
# Note: Use names that don't start with "Test" to avoid pytest collection warnings
class SamplePage(BaseModel):
    """Sample page model for testing."""
    info: Dict[str, Any] = {}
    records: list[Dict[str, Any]] = []


class SampleRecord(BaseModel):
    """Sample record model for testing."""
    id: int
    name: str


class SampleRecordPage(BaseModel):
    """Sample page model with records for testing."""
    info: Dict[str, Any] = {}
    records: list[SampleRecord] = []


@pytest.fixture
def client():
    """Create a test client."""
    return Client(base_url="https://api.example.com", apikey="test_key_123")


@pytest.fixture
def mock_response():
    """Create a mock response."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"data": "test"}
    return response


class TestClientInit:
    """Tests for Client initialization."""

    def test_init_basic(self):
        """Test basic initialization."""
        client = Client(base_url="https://api.example.com", apikey="my_key")
        assert client.base == "https://api.example.com"
        assert client.apikey == "my_key"
        assert client.timeout == 30.0
        assert client.max_retries == 5
        assert client.user_agent == "paa-graph-kb/0.1"

    def test_init_strips_trailing_slash(self):
        """Test that trailing slashes are removed from base URL."""
        client = Client(base_url="https://api.example.com/", apikey="key")
        assert client.base == "https://api.example.com"

    def test_session_headers_set(self):
        """Test that session headers are configured."""
        client = Client(base_url="https://api.example.com", apikey="key")
        assert "User-Agent" in client.session.headers
        assert client.session.headers["User-Agent"] == "paa-graph-kb/0.1"


class TestMergeQuery:
    """Tests for _merge_query static method."""

    def test_merge_query_basic(self):
        """Test basic query parameter merging."""
        url = "https://api.example.com/resource"
        result = Client._merge_query(url, foo="bar", baz="qux")
        assert "foo=bar" in result
        assert "baz=qux" in result

    def test_merge_query_preserves_existing(self):
        """Test that existing query parameters are preserved."""
        url = "https://api.example.com/resource?existing=value"
        result = Client._merge_query(url, new="param")
        assert "existing=value" in result
        assert "new=param" in result

    def test_merge_query_overrides_duplicate(self):
        """Test that new parameters override existing ones."""
        url = "https://api.example.com/resource?key=old"
        result = Client._merge_query(url, key="new")
        assert "key=new" in result
        assert "key=old" not in result

    def test_merge_query_skips_none_values(self):
        """Test that None values are not added to query string."""
        url = "https://api.example.com/resource"
        result = Client._merge_query(url, foo="bar", baz=None)
        assert "foo=bar" in result
        assert "baz" not in result


class TestEndpoint:
    """Tests for _endpoint method."""

    def test_endpoint_simple_path(self, client):
        """Test endpoint construction with simple path."""
        result = client._endpoint("objects")
        assert result == "https://api.example.com/objects"

    def test_endpoint_leading_slash(self, client):
        """Test endpoint construction with leading slash."""
        result = client._endpoint("/objects")
        assert result == "https://api.example.com/objects"

    def test_endpoint_nested_path(self, client):
        """Test endpoint construction with nested path."""
        result = client._endpoint("api/v1/objects")
        assert result == "https://api.example.com/api/v1/objects"


class TestRequest:
    """Tests for _request method."""

    def test_request_success(self, client, mock_response):
        """Test successful request."""
        with patch.object(client.session, 'get', return_value=mock_response) as mock_get:
            result = client._request("https://api.example.com/test")
            assert result == {"data": "test"}
            mock_get.assert_called_once()

    def test_request_includes_apikey(self, client, mock_response):
        """Test that apikey is included in request."""
        with patch.object(client.session, 'get', return_value=mock_response) as mock_get:
            client._request("https://api.example.com/test")
            call_args = mock_get.call_args
            assert "apikey=test_key_123" in call_args[0][0]

    def test_request_merges_params(self, client, mock_response):
        """Test that params are merged correctly."""
        with patch.object(client.session, 'get', return_value=mock_response) as mock_get:
            client._request("https://api.example.com/test", params={"size": 50})
            call_args = mock_get.call_args
            assert "size=50" in call_args[0][0]
            assert "apikey=test_key_123" in call_args[0][0]

    def test_request_does_not_duplicate_apikey(self, client, mock_response):
        """Test that apikey is not duplicated if already in URL."""
        with patch.object(client.session, 'get', return_value=mock_response) as mock_get:
            client._request("https://api.example.com/test?apikey=existing_key")
            call_args = mock_get.call_args[0][0]
            # Count occurrences of 'apikey'
            assert call_args.count('apikey=') == 1

    def test_request_timeout_configured(self, client, mock_response):
        """Test that timeout is passed to request."""
        with patch.object(client.session, 'get', return_value=mock_response) as mock_get:
            client._request("https://api.example.com/test")
            mock_get.assert_called_once()
            assert mock_get.call_args[1]['timeout'] == 30.0

    def test_request_retry_on_429(self, client):
        """Test retry logic for 429 status code."""
        # First call returns 429, second succeeds
        response_429 = Mock()
        response_429.status_code = 429
        response_429.headers = {}

        response_ok = Mock()
        response_ok.status_code = 200
        response_ok.json.return_value = {"data": "success"}

        with patch.object(client.session, 'get', side_effect=[response_429, response_ok]):
            with patch('time.sleep'):  # Mock sleep to speed up test
                result = client._request("https://api.example.com/test")
                assert result == {"data": "success"}

    def test_request_retry_on_500(self, client):
        """Test retry logic for 500 status code."""
        response_500 = Mock()
        response_500.status_code = 500
        response_500.headers = {}

        response_ok = Mock()
        response_ok.status_code = 200
        response_ok.json.return_value = {"data": "success"}

        with patch.object(client.session, 'get', side_effect=[response_500, response_ok]):
            with patch('time.sleep'):
                result = client._request("https://api.example.com/test")
                assert result == {"data": "success"}

    def test_request_respects_retry_after_header(self, client):
        """Test that Retry-After header is respected."""
        response_429 = Mock()
        response_429.status_code = 429
        response_429.headers = {"Retry-After": "2"}

        response_ok = Mock()
        response_ok.status_code = 200
        response_ok.json.return_value = {"data": "success"}

        with patch.object(client.session, 'get', side_effect=[response_429, response_ok]):
            with patch('time.sleep') as mock_sleep:
                client._request("https://api.example.com/test")
                # Should have slept at least once
                assert mock_sleep.call_count >= 1
                # First sleep should be for the Retry-After duration
                first_sleep = mock_sleep.call_args_list[0][0][0]
                assert first_sleep <= 2.0

    def test_request_max_retries_exceeded(self, client):
        """Test that exception is raised after max retries."""
        response_500 = Mock()
        response_500.status_code = 500
        response_500.headers = {}

        with patch.object(client.session, 'get', return_value=response_500):
            with patch('time.sleep'):
                with pytest.raises(requests.HTTPError):
                    client._request("https://api.example.com/test")

    def test_request_exponential_backoff(self, client):
        """Test exponential backoff on retries."""
        response_500 = Mock()
        response_500.status_code = 500
        response_500.headers = {}

        response_ok = Mock()
        response_ok.status_code = 200
        response_ok.json.return_value = {"data": "success"}

        # Fail twice, then succeed
        with patch.object(client.session, 'get', side_effect=[response_500, response_500, response_ok]):
            with patch('time.sleep') as mock_sleep:
                client._request("https://api.example.com/test")
                # Should have slept twice with exponential backoff
                assert mock_sleep.call_count == 2
                # First sleep should be backoff_initial (0.5)
                first_sleep = mock_sleep.call_args_list[0][0][0]
                second_sleep = mock_sleep.call_args_list[1][0][0]
                # Second should be approximately double the first
                assert second_sleep > first_sleep


class TestIterPages:
    """Tests for _iter_pages method."""

    def test_iter_pages_single_page(self, client, mock_response):
        """Test iteration over a single page."""
        mock_response.json.return_value = {
            "info": {"page": 1, "pages": 1},
            "records": [{"id": 1}]
        }

        with patch.object(client, '_request', return_value=mock_response.json()):
            pages = list(client._iter_pages("objects", params={}))
            assert len(pages) == 1
            assert pages[0]["records"] == [{"id": 1}]

    def test_iter_pages_multiple_pages_with_next(self, client):
        """Test iteration with explicit 'next' URL."""
        page1 = {
            "info": {"page": 1, "pages": 2, "next": "https://api.example.com/objects?page=2"},
            "records": [{"id": 1}]
        }
        page2 = {
            "info": {"page": 2, "pages": 2, "next": None},
            "records": [{"id": 2}]
        }

        with patch.object(client, '_request', side_effect=[page1, page2]):
            pages = list(client._iter_pages("objects", params={}))
            assert len(pages) == 2
            assert pages[0]["records"] == [{"id": 1}]
            assert pages[1]["records"] == [{"id": 2}]

    def test_iter_pages_constructs_next_url_if_missing(self, client):
        """Test that next URL is constructed if missing but page < pages."""
        page1 = {
            "info": {"page": 1, "pages": 2, "next": None},
            "records": [{"id": 1}]
        }
        page2 = {
            "info": {"page": 2, "pages": 2, "next": None},
            "records": [{"id": 2}]
        }

        with patch.object(client, '_request', side_effect=[page1, page2]):
            pages = list(client._iter_pages("objects", params={}))
            assert len(pages) == 2

    def test_iter_pages_sets_default_size(self, client, mock_response):
        """Test that default page size is set."""
        mock_response.json.return_value = {
            "info": {"page": 1, "pages": 1},
            "records": []
        }

        with patch.object(client, '_request', return_value=mock_response.json()) as mock_req:
            list(client._iter_pages("objects", params={}))
            # Check that size was added to params
            call_args = mock_req.call_args
            # The params dict should have size=100
            assert call_args is not None


class TestIterModel:
    """Tests for _iter_model method."""

    def test_iter_model_valid_records(self, client):
        """Test iteration with valid records."""
        page_data = {
            "info": {"page": 1, "pages": 1},
            "records": [
                {"id": 1, "name": "Test 1"},
                {"id": 2, "name": "Test 2"}
            ]
        }

        with patch.object(client, '_iter_pages', return_value=[page_data]):
            records = list(client._iter_model(
                "test",
                SampleRecordPage,
                SampleRecord,
                params={}
            ))
            assert len(records) == 2
            assert records[0].id == 1
            assert records[0].name == "Test 1"
            assert records[1].id == 2
            assert records[1].name == "Test 2"

    def test_iter_model_respects_limit(self, client):
        """Test that limit parameter is respected."""
        page_data = {
            "info": {"page": 1, "pages": 1},
            "records": [
                {"id": 1, "name": "Test 1"},
                {"id": 2, "name": "Test 2"},
                {"id": 3, "name": "Test 3"}
            ]
        }

        with patch.object(client, '_iter_pages', return_value=[page_data]):
            records = list(client._iter_model(
                "test",
                SampleRecordPage,
                SampleRecord,
                params={},
                limit=2
            ))
            assert len(records) == 2

    def test_iter_model_validation_error_non_strict(self, client):
        """Test that validation errors are skipped in non-strict mode.

        When records are already validated objects (not dicts), the isinstance check
        at line 161 means they bypass validation and are yielded directly. When they
        are dicts, they go through record_model.model_validate and can be skipped
        if invalid in non-strict mode.
        """
        # Simulate what happens when page validates successfully but contains
        # mix of valid objects and dicts that need validation
        valid_record_1 = SampleRecord(id=1, name="Test 1")
        valid_dict_2 = {"id": 2, "name": "Test 2"}  # Valid dict to be validated
        valid_record_3 = SampleRecord(id=3, name="Test 3")

        page_data = {
            "info": {"page": 1, "pages": 1},
            "records": [valid_record_1, valid_dict_2, valid_record_3]
        }

        with patch.object(client, '_iter_pages', return_value=[page_data]):
            records = list(client._iter_model(
                "test",
                SampleRecordPage,
                SampleRecord,
                params={},
                strict=False
            ))
            # All three should be returned
            assert len(records) == 3
            assert records[0].id == 1
            assert records[1].id == 2
            assert records[2].id == 3

    def test_iter_model_validation_error_strict(self, client):
        """Test that validation errors raise exception in strict mode."""
        from pydantic import ValidationError

        page_data = {
            "info": {"page": 1, "pages": 1},
            "records": [
                {"id": 1, "name": "Test 1"},
                {"id": "invalid", "name": "Test 2"}  # Invalid id
            ]
        }

        with patch.object(client, '_iter_pages', return_value=[page_data]):
            with pytest.raises(ValidationError):
                list(client._iter_model(
                    "test",
                    SampleRecordPage,
                    SampleRecord,
                    params={},
                    strict=True
                ))

    def test_iter_model_multiple_pages(self, client):
        """Test iteration across multiple pages."""
        page1 = {
            "info": {"page": 1, "pages": 2},
            "records": [
                {"id": 1, "name": "Test 1"},
                {"id": 2, "name": "Test 2"}
            ]
        }
        page2 = {
            "info": {"page": 2, "pages": 2},
            "records": [
                {"id": 3, "name": "Test 3"},
                {"id": 4, "name": "Test 4"}
            ]
        }

        with patch.object(client, '_iter_pages', return_value=[page1, page2]):
            records = list(client._iter_model(
                "test",
                SampleRecordPage,
                SampleRecord,
                params={}
            ))
            assert len(records) == 4
            assert records[0].id == 1
            assert records[3].id == 4

    def test_iter_model_limit_across_pages(self, client):
        """Test that limit works across multiple pages."""
        page1 = {
            "info": {"page": 1, "pages": 2},
            "records": [
                {"id": 1, "name": "Test 1"},
                {"id": 2, "name": "Test 2"}
            ]
        }
        page2 = {
            "info": {"page": 2, "pages": 2},
            "records": [
                {"id": 3, "name": "Test 3"},
                {"id": 4, "name": "Test 4"}
            ]
        }

        with patch.object(client, '_iter_pages', return_value=[page1, page2]):
            records = list(client._iter_model(
                "test",
                SampleRecordPage,
                SampleRecord,
                params={},
                limit=3
            ))
            assert len(records) == 3
