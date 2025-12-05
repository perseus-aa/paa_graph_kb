"""Tests for the GettyClient class."""
from __future__ import annotations

import os
from unittest.mock import MagicMock, Mock, patch

import pytest
from SPARQLWrapper import JSON

from paa_graph_kb.clients.getty_client import GettyClient
from paa_graph_kb.models.getty.models import GettyObject, GettyPerson


@pytest.fixture
def getty_client():
    """Create a GettyClient instance."""
    return GettyClient()


@pytest.fixture
def mock_sparql_response_objects():
    """Mock SPARQL response for objects."""
    return {
        "results": {
            "bindings": [
                {
                    "s": {
                        "type": "uri",
                        "value": "http://data.getty.edu/museum/collection/object/123"
                    }
                },
                {
                    "s": {
                        "type": "uri",
                        "value": "http://data.getty.edu/museum/collection/object/456"
                    }
                }
            ]
        }
    }


@pytest.fixture
def mock_sparql_response_people():
    """Mock SPARQL response for people."""
    return {
        "results": {
            "bindings": [
                {
                    "s": {
                        "type": "uri",
                        "value": "http://data.getty.edu/museum/collection/person/789"
                    }
                }
            ]
        }
    }


@pytest.fixture
def mock_object_data():
    """Sample Getty object data (Linked Art JSON-LD style)."""
    return {
        "id": "http://data.getty.edu/museum/collection/object/123",
        "type": "HumanMadeObject",
        "_label": "The Irises",
        "identified_by": [
            {
                "type": "Name",
                "_content": "The Irises"
            },
            {
                "type": "Identifier",
                "_content": "90.PA.20",
                "_label": "Accession Number"
            }
        ]
    }


@pytest.fixture
def mock_person_data():
    """Sample Getty person data."""
    return {
        "id": "http://data.getty.edu/museum/collection/person/789",
        "type": "Person",
        "_label": "Vincent van Gogh",
        "identified_by": [
            {
                "type": "Name",
                "_content": "Vincent van Gogh"
            }
        ]
    }


class TestGettyClientInit:
    """Tests for GettyClient initialization."""

    def test_init_defaults(self):
        """Test initialization with defaults."""
        client = GettyClient()
        assert client.base == "https://data.getty.edu/museum/collection/sparql"
        assert client.sparql_endpoint == "https://data.getty.edu/museum/collection/sparql"
        assert client.apikey is None

    def test_init_custom_cache(self):
        """Test initialization with custom cache directory."""
        client = GettyClient(cache_dir="/tmp/custom_cache")
        assert str(client.cache_dir) == "/tmp/custom_cache"


class TestIterObjects:
    """Tests for iter_objects method."""

    @patch("paa_graph_kb.clients.getty_client.SPARQLWrapper")
    def test_iter_objects_flow(self, mock_sparql_cls, getty_client, mock_sparql_response_objects, mock_object_data):
        """Test the full flow: SPARQL discovery -> HTTP retrieval -> Model parsing."""
        
        # 1. Mock SPARQL
        mock_sparql = Mock()
        mock_sparql_cls.return_value = mock_sparql
        # Return results once, then empty to stop pagination
        mock_sparql.query.return_value.convert.side_effect = [
            mock_sparql_response_objects, 
            {"results": {"bindings": []}}
        ]

        # 2. Mock HTTP retrieval (self._request)
        with patch.object(getty_client, '_request', return_value=mock_object_data) as mock_request:
            
            # Run iterator
            objects = list(getty_client.iter_objects(size=2))
            
            # Assertions
            assert len(objects) == 2
            assert isinstance(objects[0], GettyObject)
            assert objects[0].id == "http://data.getty.edu/museum/collection/object/123"
            assert objects[0].label == "The Irises"
            
            # Verify SPARQL was called
            assert mock_sparql.setQuery.call_count >= 1
            assert mock_sparql.setReturnFormat.call_count >= 1
            mock_sparql.setReturnFormat.assert_called_with(JSON)
            
            # Verify HTTP requests were made for the specific objects
            mock_request.assert_any_call("http://data.getty.edu/museum/collection/object/123")
            mock_request.assert_any_call("http://data.getty.edu/museum/collection/object/456")

    @patch("paa_graph_kb.clients.getty_client.SPARQLWrapper")
    def test_iter_objects_sparql_error(self, mock_sparql_cls, getty_client):
        """Test handling of SPARQL errors."""
        mock_sparql = Mock()
        mock_sparql_cls.return_value = mock_sparql
        mock_sparql.query.side_effect = Exception("SPARQL connection failed")

        objects = list(getty_client.iter_objects())
        assert len(objects) == 0

    @patch("paa_graph_kb.clients.getty_client.SPARQLWrapper")
    def test_iter_objects_http_error(self, mock_sparql_cls, getty_client, mock_sparql_response_objects):
        """Test handling of HTTP retrieval errors for individual objects."""
        mock_sparql = Mock()
        mock_sparql_cls.return_value = mock_sparql
        # Return results once, then empty to stop pagination
        mock_sparql.query.return_value.convert.side_effect = [
            mock_sparql_response_objects,
            {"results": {"bindings": []}}
        ]

        # Simulate request failure
        with patch.object(getty_client, '_request', side_effect=Exception("HTTP 404")):
            objects = list(getty_client.iter_objects(size=2))
            # Should yield 0 objects but not crash
            assert len(objects) == 0

    @patch("paa_graph_kb.clients.getty_client.SPARQLWrapper")
    def test_iter_objects_limit(self, mock_sparql_cls, getty_client, mock_sparql_response_objects, mock_object_data):
        """Test respecting the limit parameter."""
        mock_sparql = Mock()
        mock_sparql_cls.return_value = mock_sparql
        mock_sparql.query.return_value.convert.return_value = mock_sparql_response_objects

        with patch.object(getty_client, '_request', return_value=mock_object_data):
            objects = list(getty_client.iter_objects(limit=1))
            assert len(objects) == 1


class TestIterPeople:
    """Tests for iter_people method."""

    @patch("paa_graph_kb.clients.getty_client.SPARQLWrapper")
    def test_iter_people_flow(self, mock_sparql_cls, getty_client, mock_sparql_response_people, mock_person_data):
        """Test fetching people."""
        mock_sparql = Mock()
        mock_sparql_cls.return_value = mock_sparql
        mock_sparql.query.return_value.convert.side_effect = [
            mock_sparql_response_people,
            {"results": {"bindings": []}}
        ]

        with patch.object(getty_client, '_request', return_value=mock_person_data) as mock_request:
            people = list(getty_client.iter_people())
            
            assert len(people) == 1
            assert isinstance(people[0], GettyPerson)
            assert people[0].label == "Vincent van Gogh"
            
            mock_request.assert_called_with("http://data.getty.edu/museum/collection/person/789")
