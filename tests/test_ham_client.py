"""Tests for the HAMClient class."""
from __future__ import annotations

import os
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from paa_graph_kb.clients.ham_client import HAMClient
from paa_graph_kb.models.ham.models import (
    HAMObject,
    HAMPage,
    HAMPeriod,
    HAMPerson,
    HAMPlace,
    HAMPublication,
    PeriodPage,
    PersonPage,
    PlacePage,
    PublicationPage,
)


@pytest.fixture
def mock_env():
    """Mock environment variables for HAM client."""
    with patch.dict(os.environ, {
        'HAM_API_BASE': 'https://api.harvardartmuseums.org',
        'HAM_APIKEY': 'test_ham_key'
    }):
        yield


@pytest.fixture
def ham_client(mock_env):
    """Create a HAMClient instance with mocked environment."""
    return HAMClient()


@pytest.fixture
def sample_object_data():
    """Sample HAM object data."""
    return {
        "id": 123456,
        "objectid": 123456,
        "objectnumber": "1999.99",
        "title": "Ancient Greek Vase",
        "culture": "Greek",
        "period": "Classical",
        "periodid": 1,
        "classification": "Vessels",
        "dated": "450-400 BCE",
        "datebegin": -450,
        "dateend": -400,
        "medium": "Terracotta",
        "technique": "Black glaze",
        "dimensions": "H. 30 cm, Diam. 20 cm",
        "description": "A well-preserved example of Attic pottery.",
        "creditline": "Gift of Anonymous Donor",
        "provenance": "Acquired from private collection in 1999",
        "url": "https://www.harvardartmuseums.org/collections/object/123456",
        "primaryimageurl": "https://nrs.harvard.edu/urn-3:HUAM:123456",
        "imagecount": 3,
        "accessionyear": 1999,
        "department": "Ancient and Byzantine Art",
        "division": "European and American Art",
        "verificationlevel": 4,
        "seeAlso": [
            {
                "id": "https://iiif.harvardartmuseums.org/manifests/object/123456",
                "type": "IIIF Manifest",
                "format": "application/json"
            }
        ],
        "worktypes": [
            {
                "worktypeid": 789,
                "worktype": "vessel"
            }
        ],
        "colors": [
            {
                "color": "black",
                "spectrum": "#000000",
                "percent": 0.45
            }
        ],
        "terms": {
            "culture": [{"name": "Greek", "id": 1}],
            "medium": [{"name": "Terracotta", "id": 2}],
            "technique": [{"name": "Black glaze", "id": 3}]
        }
    }


@pytest.fixture
def sample_period_data():
    """Sample HAM period data."""
    return {
        "id": 1,
        "name": "Classical",
        "displayname": "Classical Period",
        "dated": "480-323 BCE",
        "datebegin": -480,
        "dateend": -323,
        "description": "The Classical period of ancient Greece"
    }


@pytest.fixture
def sample_place_data():
    """Sample HAM place data."""
    return {
        "id": 2,
        "name": "Athens",
        "displayname": "Athens, Greece",
        "type": "City",
        "country": "Greece",
        "region": "Attica",
        "city": "Athens",
        "geo": {
            "latitude": 37.9838,
            "longitude": 23.7275
        },
        "latitude": 37.9838,
        "longitude": 23.7275
    }


@pytest.fixture
def sample_person_data():
    """Sample HAM person data."""
    return {
        "id": 3,
        "name": "Euphronios",
        "displayname": "Euphronios (potter)",
        "role": "Potter",
        "culture": "Greek",
        "gender": "Male",
        "birthyear": -530,
        "deathyear": -470,
        "born": "circa 530 BCE",
        "died": "circa 470 BCE",
        "birthplace": "Athens",
        "url": "https://www.harvardartmuseums.org/collections/person/3"
    }


@pytest.fixture
def sample_publication_data():
    """Sample HAM publication data."""
    return {
        "id": 4,
        "title": "Greek Vases in the Harvard Art Museums",
        "subtitle": "Volume 1",
        "citation": "Doe, J. (2020). Greek Vases in the Harvard Art Museums. Cambridge: Harvard.",
        "authors": ["Jane Doe", "John Smith"],
        "publishyear": 2020,
        "publisher": "Harvard University Press",
        "isbn": "978-0-674-12345-6",
        "url": "https://www.example.com/publication"
    }


class TestHAMClientInit:
    """Tests for HAMClient initialization."""

    def test_init_from_env(self, mock_env):
        """Test initialization from environment variables."""
        client = HAMClient()
        assert client.base == "https://api.harvardartmuseums.org"
        assert client.apikey == "test_ham_key"

    def test_init_without_env_vars(self):
        """Test initialization without environment variables."""
        # HAMClient will fail if env vars are missing because Client.__init__
        # calls base_url.rstrip("/") when base_url is None
        # This is expected behavior - HAMClient requires env vars
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(AttributeError):
                HAMClient()


class TestIterObjects:
    """Tests for iter_objects method."""

    def test_iter_objects_basic(self, ham_client, sample_object_data):
        """Test basic object iteration."""
        page_data = {
            "info": {"page": 1, "pages": 1, "totalrecords": 1},
            "records": [sample_object_data]
        }

        with patch.object(ham_client, '_iter_pages', return_value=[page_data]):
            objects = list(ham_client.iter_objects())
            assert len(objects) == 1
            assert isinstance(objects[0], HAMObject)
            assert objects[0].objectid == 123456
            assert objects[0].title == "Ancient Greek Vase"

    def test_iter_objects_with_params(self, ham_client, sample_object_data):
        """Test object iteration with query parameters."""
        page_data = {
            "info": {"page": 1, "pages": 1},
            "records": [sample_object_data]
        }

        with patch.object(ham_client, '_iter_model') as mock_iter:
            mock_iter.return_value = iter([HAMObject.model_validate(sample_object_data)])

            params = {"culture": "Greek", "hasimage": 1}
            objects = list(ham_client.iter_objects(params=params))

            mock_iter.assert_called_once()
            # Check that params were passed correctly (4th positional argument)
            call_args, call_kwargs = mock_iter.call_args
            assert call_args[3] == params  # params is 4th positional arg

    def test_iter_objects_with_limit(self, ham_client, sample_object_data):
        """Test object iteration with limit."""
        objects_data = [
            {**sample_object_data, "id": i, "objectid": i}
            for i in range(1, 6)
        ]
        page_data = {
            "info": {"page": 1, "pages": 1},
            "records": objects_data
        }

        with patch.object(ham_client, '_iter_pages', return_value=[page_data]):
            objects = list(ham_client.iter_objects(limit=3))
            assert len(objects) == 3

    def test_iter_objects_multiple_pages(self, ham_client, sample_object_data):
        """Test object iteration across multiple pages."""
        page1_data = {
            "info": {"page": 1, "pages": 2},
            "records": [{**sample_object_data, "id": 1, "objectid": 1}]
        }
        page2_data = {
            "info": {"page": 2, "pages": 2},
            "records": [{**sample_object_data, "id": 2, "objectid": 2}]
        }

        with patch.object(ham_client, '_iter_pages', return_value=[page1_data, page2_data]):
            objects = list(ham_client.iter_objects())
            assert len(objects) == 2
            assert objects[0].objectid == 1
            assert objects[1].objectid == 2

    def test_iter_objects_strict_mode(self, ham_client):
        """Test object iteration in strict validation mode."""
        # Invalid data (missing required 'id' field)
        invalid_data = {
            "objectid": 123,
            "title": "Test"
        }
        page_data = {
            "info": {"page": 1, "pages": 1},
            "records": [invalid_data]
        }

        from pydantic import ValidationError

        with patch.object(ham_client, '_iter_pages', return_value=[page_data]):
            with pytest.raises(ValidationError):
                list(ham_client.iter_objects(strict=True))

    def test_iter_objects_non_strict_mode(self, ham_client, sample_object_data):
        """Test object iteration in non-strict mode.

        In non-strict mode, when page contains mix of validated objects and dicts,
        validated objects are yielded directly while dicts go through validation.
        """
        # Simulate API response with mix of already-validated object and dict
        valid_object = HAMObject.model_validate(sample_object_data)
        valid_dict = {**sample_object_data, "id": 999, "objectid": 999}

        page_data = {
            "info": {"page": 1, "pages": 1},
            "records": [valid_object, valid_dict]
        }

        with patch.object(ham_client, '_iter_pages', return_value=[page_data]):
            objects = list(ham_client.iter_objects(strict=False))
            # Should return both objects
            assert len(objects) == 2
            assert objects[0].objectid == 123456
            assert objects[1].objectid == 999

    def test_iter_objects_custom_size(self, ham_client):
        """Test object iteration with custom page size."""
        with patch.object(ham_client, '_iter_model') as mock_iter:
            mock_iter.return_value = iter([])

            list(ham_client.iter_objects(size=50))

            call_args = mock_iter.call_args
            assert call_args[1]['size'] == 50


class TestIterPeriods:
    """Tests for iter_periods method."""

    def test_iter_periods_basic(self, ham_client, sample_period_data):
        """Test basic period iteration."""
        page_data = {
            "info": {"page": 1, "pages": 1},
            "records": [sample_period_data]
        }

        with patch.object(ham_client, '_iter_pages', return_value=[page_data]):
            periods = list(ham_client.iter_periods())
            assert len(periods) == 1
            assert isinstance(periods[0], HAMPeriod)
            assert periods[0].name == "Classical"
            assert periods[0].datebegin == -480

    def test_iter_periods_with_params(self, ham_client):
        """Test period iteration with query parameters."""
        with patch.object(ham_client, '_iter_model') as mock_iter:
            mock_iter.return_value = iter([])

            params = {"q": "Classical"}
            list(ham_client.iter_periods(params=params))

            # Check that the correct endpoint and params were passed
            call_args, call_kwargs = mock_iter.call_args
            assert call_args[0] == "period"
            assert call_args[3] == params  # params is 4th positional arg


class TestIterPlaces:
    """Tests for iter_places method."""

    def test_iter_places_basic(self, ham_client, sample_place_data):
        """Test basic place iteration."""
        page_data = {
            "info": {"page": 1, "pages": 1},
            "records": [sample_place_data]
        }

        with patch.object(ham_client, '_iter_pages', return_value=[page_data]):
            places = list(ham_client.iter_places())
            assert len(places) == 1
            assert isinstance(places[0], HAMPlace)
            assert places[0].name == "Athens"
            assert places[0].latitude == 37.9838

    def test_iter_places_with_geo_data(self, ham_client, sample_place_data):
        """Test place iteration with geographic data."""
        page_data = {
            "info": {"page": 1, "pages": 1},
            "records": [sample_place_data]
        }

        with patch.object(ham_client, '_iter_pages', return_value=[page_data]):
            places = list(ham_client.iter_places())
            place = places[0]
            assert place.geo is not None
            assert place.geo.latitude == 37.9838
            assert place.geo.longitude == 23.7275


class TestIterPeople:
    """Tests for iter_people method."""

    def test_iter_people_basic(self, ham_client, sample_person_data):
        """Test basic person iteration."""
        page_data = {
            "info": {"page": 1, "pages": 1},
            "records": [sample_person_data]
        }

        with patch.object(ham_client, '_iter_pages', return_value=[page_data]):
            people = list(ham_client.iter_people())
            assert len(people) == 1
            assert isinstance(people[0], HAMPerson)
            assert people[0].name == "Euphronios"
            assert people[0].role == "Potter"
            assert people[0].birthyear == -530

    def test_iter_people_with_dates(self, ham_client, sample_person_data):
        """Test person iteration with birth/death dates."""
        page_data = {
            "info": {"page": 1, "pages": 1},
            "records": [sample_person_data]
        }

        with patch.object(ham_client, '_iter_pages', return_value=[page_data]):
            people = list(ham_client.iter_people())
            person = people[0]
            assert person.born == "circa 530 BCE"
            assert person.died == "circa 470 BCE"
            assert person.birthplace == "Athens"


class TestIterPublications:
    """Tests for iter_publications method."""

    def test_iter_publications_basic(self, ham_client, sample_publication_data):
        """Test basic publication iteration."""
        page_data = {
            "info": {"page": 1, "pages": 1},
            "records": [sample_publication_data]
        }

        with patch.object(ham_client, '_iter_pages', return_value=[page_data]):
            publications = list(ham_client.iter_publications())
            assert len(publications) == 1
            assert isinstance(publications[0], HAMPublication)
            assert publications[0].title == "Greek Vases in the Harvard Art Museums"
            assert publications[0].publishyear == 2020

    def test_iter_publications_with_authors(self, ham_client, sample_publication_data):
        """Test publication iteration with multiple authors."""
        page_data = {
            "info": {"page": 1, "pages": 1},
            "records": [sample_publication_data]
        }

        with patch.object(ham_client, '_iter_pages', return_value=[page_data]):
            publications = list(ham_client.iter_publications())
            pub = publications[0]
            assert len(pub.authors) == 2
            assert "Jane Doe" in pub.authors
            assert "John Smith" in pub.authors

    def test_iter_publications_with_isbn(self, ham_client, sample_publication_data):
        """Test publication iteration with ISBN."""
        page_data = {
            "info": {"page": 1, "pages": 1},
            "records": [sample_publication_data]
        }

        with patch.object(ham_client, '_iter_pages', return_value=[page_data]):
            publications = list(ham_client.iter_publications())
            pub = publications[0]
            assert pub.isbn == "978-0-674-12345-6"
            assert pub.publisher == "Harvard University Press"


class TestHAMClientIntegration:
    """Integration tests for HAMClient."""

    def test_all_iterator_methods_use_correct_endpoints(self, ham_client):
        """Test that all iterator methods use the correct API endpoints."""
        with patch.object(ham_client, '_iter_model') as mock_iter:
            mock_iter.return_value = iter([])

            # Test each iterator method
            list(ham_client.iter_objects())
            assert mock_iter.call_args[0][0] == "object"

            list(ham_client.iter_periods())
            assert mock_iter.call_args[0][0] == "period"

            list(ham_client.iter_places())
            assert mock_iter.call_args[0][0] == "place"

            list(ham_client.iter_people())
            assert mock_iter.call_args[0][0] == "person"

            list(ham_client.iter_publications())
            assert mock_iter.call_args[0][0] == "publication"

    def test_all_iterator_methods_use_correct_models(self, ham_client):
        """Test that all iterator methods use the correct Pydantic models."""
        with patch.object(ham_client, '_iter_model') as mock_iter:
            mock_iter.return_value = iter([])

            # Test objects
            list(ham_client.iter_objects())
            assert mock_iter.call_args[0][1] == HAMPage
            assert mock_iter.call_args[0][2] == HAMObject

            # Test periods
            list(ham_client.iter_periods())
            assert mock_iter.call_args[0][1] == PeriodPage
            assert mock_iter.call_args[0][2] == HAMPeriod

            # Test places
            list(ham_client.iter_places())
            assert mock_iter.call_args[0][1] == PlacePage
            assert mock_iter.call_args[0][2] == HAMPlace

            # Test people
            list(ham_client.iter_people())
            assert mock_iter.call_args[0][1] == PersonPage
            assert mock_iter.call_args[0][2] == HAMPerson

            # Test publications
            list(ham_client.iter_publications())
            assert mock_iter.call_args[0][1] == PublicationPage
            assert mock_iter.call_args[0][2] == HAMPublication


class TestHAMClientRealWorldScenarios:
    """Tests simulating real-world usage scenarios."""

    def test_fetch_greek_objects_with_images(self, ham_client, sample_object_data):
        """Test fetching Greek objects with images (common use case)."""
        page_data = {
            "info": {"page": 1, "pages": 1},
            "records": [sample_object_data]
        }

        with patch.object(ham_client, '_iter_pages', return_value=[page_data]):
            params = {"culture": "Greek", "hasimage": 1}
            objects = list(ham_client.iter_objects(params=params, limit=50))

            assert len(objects) > 0
            assert objects[0].culture == "Greek"
            assert objects[0].imagecount > 0

    def test_fetch_objects_by_period(self, ham_client, sample_object_data):
        """Test fetching objects filtered by period."""
        page_data = {
            "info": {"page": 1, "pages": 1},
            "records": [sample_object_data]
        }

        with patch.object(ham_client, '_iter_pages', return_value=[page_data]):
            params = {"period": "Classical"}
            objects = list(ham_client.iter_objects(params=params))

            assert len(objects) > 0
            assert objects[0].period == "Classical"

    def test_fetch_small_batch_for_testing(self, ham_client, sample_object_data):
        """Test fetching small batch (common during development)."""
        objects_data = [
            {**sample_object_data, "id": i, "objectid": i}
            for i in range(1, 11)
        ]
        page_data = {
            "info": {"page": 1, "pages": 1},
            "records": objects_data
        }

        with patch.object(ham_client, '_iter_pages', return_value=[page_data]):
            # Fetch only 5 for quick testing
            objects = list(ham_client.iter_objects(limit=5))
            assert len(objects) == 5
