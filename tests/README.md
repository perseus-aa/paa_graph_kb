# Test Suite

This directory contains comprehensive tests for the Perseus Linked Art / CIDOC-CRM integration project.

## Test Files

### `test_client.py`
Tests for the base `Client` class covering:
- HTTP client initialization and configuration
- URL and query parameter handling
- Request retry logic with exponential backoff
- Pagination across single and multiple pages
- Pydantic model validation (strict and non-strict modes)
- Error handling and edge cases

**28 test methods across 6 test classes**

### `test_ham_client.py`
Tests for the `HAMClient` class covering:
- HAMClient initialization from environment variables
- All five iterator methods (objects, periods, places, people, publications)
- Query parameter filtering and pagination
- Validation modes (strict vs. non-strict)
- Real-world usage scenarios (Greek objects with images, period filtering, batch operations)

**23 test methods across 9 test classes**

## Running Tests

### Prerequisites

Install dependencies using PDM:

```bash
pdm install
```

This will install all dependencies from `pyproject.toml`, including the dev dependencies:
- pytest
- pytest-cov
- pytest-mock

### Run All Tests

```bash
pdm run pytest tests/ -v
```

### Run Specific Test Files

```bash
# Test only the Client class
pdm run pytest tests/test_client.py -v

# Test only the HAMClient class
pdm run pytest tests/test_ham_client.py -v
```

### Run with Coverage

```bash
pdm run pytest tests/ --cov=paa_graph_kb --cov-report=html
```

Then open `htmlcov/index.html` in your browser to view the coverage report.

### Run Specific Test Classes or Methods

```bash
# Run a specific test class
pdm run pytest tests/test_client.py::TestClientInit -v

# Run a specific test method
pdm run pytest tests/test_client.py::TestClientInit::test_init_basic -v
```

## Test Organization

Tests are organized by the component they test:

- **TestClientInit**: Client initialization
- **TestMergeQuery**: URL query parameter merging
- **TestEndpoint**: Endpoint URL construction
- **TestRequest**: HTTP request handling
- **TestIterPages**: Page iteration logic
- **TestIterModel**: Model iteration with validation
- **TestHAMClientInit**: HAMClient initialization
- **TestIterObjects**: Object iteration
- **TestIterPeriods**: Period iteration
- **TestIterPlaces**: Place iteration
- **TestIterPeople**: People iteration
- **TestIterPublications**: Publication iteration
- **TestHAMClientIntegration**: Integration tests
- **TestHAMClientRealWorldScenarios**: Real-world usage patterns

## Mocking Strategy

Tests use `unittest.mock` and `pytest-mock` to:
- Mock HTTP requests to avoid actual API calls
- Mock environment variables for configuration
- Simulate various response scenarios (success, errors, retries)
- Test edge cases without external dependencies

## Test Fixtures

Common fixtures are defined in `conftest.py`:
- Python path configuration
- Shared test data structures
- Mock environment setup

## Adding New Tests

When adding new tests:

1. Follow the existing naming convention: `test_<feature>.py`
2. Use descriptive test method names: `test_<what_it_tests>`
3. Include docstrings explaining what each test validates
4. Group related tests in test classes
5. Use fixtures for common setup
6. Mock external dependencies

## Continuous Integration

These tests are designed to run in CI/CD pipelines:
- No external API dependencies (all mocked)
- Fast execution (< 1 second per test)
- Clear, descriptive output
- Proper error messages on failure

## Coverage Goals

Current test coverage targets:
- **Client class**: 100% coverage of public methods
- **HAMClient class**: 100% coverage of public methods
- **Edge cases**: Comprehensive coverage of error paths and boundary conditions

## Future Test Additions

Recommended additions:
1. **SPARQL template tests**: Validate template syntax and transformations
2. **Integration tests**: Test full pipeline from API to CRM graph
3. **Performance tests**: Benchmark pagination and transformation speed
4. **Validation tests**: Test SHACL validation with generated graphs
