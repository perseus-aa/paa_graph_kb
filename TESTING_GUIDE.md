# Testing Guide

This guide explains how to run the comprehensive test suite for the Perseus Linked Art / CIDOC-CRM integration project.

## Quick Start

```bash
# Install dependencies (if not already installed)
pdm install

# Run all tests
pdm run pytest tests/ -v

# Run with coverage report
pdm run pytest tests/ --cov=paa_graph_kb --cov-report=term-missing
```

## Test Suite Overview

The test suite includes **51 test cases** covering:

### Client Tests (`test_client.py` - 28 tests)
- ✅ Initialization and configuration
- ✅ URL construction and query parameter merging
- ✅ HTTP request handling with retry logic
- ✅ Exponential backoff on failures
- ✅ Retry-After header handling
- ✅ Pagination across single and multiple pages
- ✅ Automatic next URL construction
- ✅ Pydantic model validation (strict/non-strict modes)
- ✅ Limit enforcement across pages
- ✅ Error handling and edge cases

### HAMClient Tests (`test_ham_client.py` - 23 tests)
- ✅ Environment variable configuration
- ✅ Object iteration with filtering
- ✅ Period iteration
- ✅ Place iteration with geographic data
- ✅ People iteration with biographical data
- ✅ Publication iteration with bibliographic data
- ✅ Query parameter handling
- ✅ Pagination and page size configuration
- ✅ Validation modes (strict/non-strict)
- ✅ Real-world scenarios (Greek objects, filtering, batch operations)
- ✅ Integration tests for all endpoints

## Running Tests

### All Tests
```bash
pdm run pytest tests/ -v
```

### Specific Test File
```bash
pdm run pytest tests/test_client.py -v
pdm run pytest tests/test_ham_client.py -v
```

### Specific Test Class
```bash
pdm run pytest tests/test_client.py::TestClientInit -v
pdm run pytest tests/test_ham_client.py::TestIterObjects -v
```

### Specific Test Method
```bash
pdm run pytest tests/test_client.py::TestRequest::test_request_retry_on_429 -v
```

### With Coverage
```bash
# Terminal report
pdm run pytest tests/ --cov=paa_graph_kb --cov-report=term-missing

# HTML report
pdm run pytest tests/ --cov=paa_graph_kb --cov-report=html
open htmlcov/index.html  # View in browser
```

### Watch Mode (for development)
```bash
pdm run pytest-watch tests/
```

## Test Output Examples

### Successful Test Run
```
tests/test_client.py::TestClientInit::test_init_basic PASSED
tests/test_client.py::TestClientInit::test_init_strips_trailing_slash PASSED
tests/test_client.py::TestRequest::test_request_success PASSED
tests/test_client.py::TestRequest::test_request_retry_on_429 PASSED
...
======================== 51 passed in 2.34s ========================
```

### Failed Test
```
tests/test_client.py::TestRequest::test_request_success FAILED

============================== FAILURES ==============================
______________________ TestRequest.test_request_success ______________

    def test_request_success(self, client, mock_response):
>       assert result == {"data": "test"}
E       AssertionError: assert {'data': 'wrong'} == {'data': 'test'}

tests/test_client.py:123: AssertionError
```

## Test Coverage Report

After running with `--cov-report=term-missing`, you'll see:

```
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
src/paa_graph_kb/clients/ham_client.py    145      5    97%   87-91
tests/test_client.py                      412      0   100%
tests/test_ham_client.py                  347      0   100%
---------------------------------------------------------------------
TOTAL                                     904      5    99%
```

## Environment Setup

Tests automatically handle environment setup:

1. **Python path**: Configured in `conftest.py`
2. **Environment variables**: Mocked in individual tests
3. **HTTP requests**: Mocked to avoid actual API calls

## Test Data

Tests use realistic sample data:

```python
sample_object_data = {
    "id": 123456,
    "objectid": 123456,
    "title": "Ancient Greek Vase",
    "culture": "Greek",
    "period": "Classical",
    # ... more fields
}
```

This ensures tests validate real-world scenarios.

## Mocking Strategy

### HTTP Requests
```python
with patch.object(client.session, 'get', return_value=mock_response):
    result = client._request("https://api.example.com/test")
```

### Environment Variables
```python
with patch.dict(os.environ, {'HAM_API_BASE': 'https://test.com'}):
    client = HAMClient()
```

### Time-Based Operations
```python
with patch('time.sleep'):  # Speed up retry tests
    client._request("https://api.example.com/test")
```

## Debugging Tests

### Run with Python Debugger
```bash
pdm run pytest tests/test_client.py::TestRequest::test_request_retry_on_429 --pdb
```

### Show Print Statements
```bash
pdm run pytest tests/ -v -s
```

### Show Local Variables on Failure
```bash
pdm run pytest tests/ -v -l
```

### Stop on First Failure
```bash
pdm run pytest tests/ -v -x
```

## Writing New Tests

### Test Structure
```python
class TestNewFeature:
    """Tests for new feature."""

    def test_basic_functionality(self):
        """Test basic functionality."""
        # Arrange
        client = Client(base_url="https://api.example.com", apikey="key")

        # Act
        result = client.do_something()

        # Assert
        assert result == expected_value
```

### Using Fixtures
```python
@pytest.fixture
def configured_client():
    """Create a pre-configured client."""
    return Client(base_url="https://api.example.com", apikey="test_key")

def test_with_fixture(configured_client):
    """Test using fixture."""
    result = configured_client.do_something()
    assert result is not None
```

### Parameterized Tests
```python
@pytest.mark.parametrize("input,expected", [
    ("http://example.com", "http://example.com"),
    ("http://example.com/", "http://example.com"),
    ("https://api.test.org/", "https://api.test.org"),
])
def test_url_normalization(input, expected):
    """Test URL normalization with various inputs."""
    client = Client(base_url=input, apikey="key")
    assert client.base == expected
```

## Continuous Integration

Tests are designed for CI/CD:

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: pdm-project/setup-pdm@v3
      - run: pdm install
      - run: pdm run pytest tests/ --cov --cov-report=xml
      - uses: codecov/codecov-action@v3
```

### GitLab CI Example
```yaml
test:
  image: python:3.12
  before_script:
    - pip install pdm
    - pdm install
  script:
    - pdm run pytest tests/ --cov --cov-report=term
```

## Performance Considerations

Tests are designed to be fast:
- **No real API calls**: All HTTP requests are mocked
- **No sleep delays**: Time-based operations are mocked
- **Minimal data**: Sample data is kept small
- **Isolated**: Each test is independent

Typical test suite execution time: **< 5 seconds**

## Troubleshooting

### Import Errors
```bash
# Make sure you're in the project root
cd /path/to/paa_graph_kb

# Install dependencies
pdm install

# Verify Python path
pdm run python -c "import sys; print(sys.path)"
```

### Module Not Found
If you see `ModuleNotFoundError: No module named 'paa_graph_kb'`:

1. Check `pytest.ini` has correct `pythonpath` setting
2. Run tests with `pdm run pytest` (not just `pytest`)
3. Verify dependencies are installed: `pdm list`

### Test Failures After Changes
If tests fail after modifying code:

1. Check if mock setups need updating
2. Verify method signatures haven't changed
3. Update test expectations if behavior changed intentionally
4. Run specific failing test with `-v -s` for more details

## Next Steps

After verifying these tests pass:

1. **Add SPARQL template tests**: Validate template syntax and transformations
2. **Integration tests**: Test full staging → CRM transformation pipeline
3. **End-to-end tests**: Test with small batch of real HAM data
4. **Performance tests**: Benchmark large dataset processing

## Questions or Issues?

If you encounter issues:
1. Check test output with `-v` flag for details
2. Review test code and docstrings for expected behavior
3. Verify all dependencies are installed: `pdm install`
4. Check that you're using Python 3.12+ as specified in `pyproject.toml`
