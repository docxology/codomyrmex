# Scrape Module Test Suite

## Overview

Comprehensive test suite for the scrape module, covering all core functionality, Firecrawl integration, and edge cases.

## Test Structure

```
tests/
├── unit/
│   ├── test_core.py          # Core abstractions (ScrapeResult, ScrapeOptions, etc.)
│   ├── test_scraper.py       # Main Scraper class
│   ├── test_firecrawl.py     # FirecrawlClient and FirecrawlAdapter
│   └── test_config.py        # Configuration management
└── integration/
    └── test_scrape_integration.py  # End-to-end tests (requires API key)
```

## Test Coverage

### Core Abstractions (`test_core.py`)
- ✅ `ScrapeFormat` enum values
- ✅ `ScrapeResult` creation and methods
- ✅ `ScrapeOptions` configuration
- ✅ `CrawlResult`, `MapResult`, `SearchResult`, `ExtractResult`
- ✅ `BaseScraper` abstract class

### Scraper Class (`test_scraper.py`)
- ✅ Initialization with adapter
- ✅ Initialization with config only
- ✅ Default adapter creation (Firecrawl)
- ✅ Error handling when no adapter available
- ✅ `scrape()` method with various options
- ✅ `crawl()` method with options
- ✅ `map()` method with and without search
- ✅ `search()` method with options
- ✅ `extract()` method with schema and prompt
- ✅ Input validation for all methods
- ✅ Error propagation

### Firecrawl Integration (`test_firecrawl.py`)

#### FirecrawlClient
- ✅ Initialization without firecrawl-py package
- ✅ Initialization without API key
- ✅ Successful initialization
- ✅ `scrape_url()` with various formats and actions
- ✅ `scrape_url()` timeout error handling
- ✅ `scrape_url()` connection error handling
- ✅ `crawl_url()` success and error cases
- ✅ `map_url()` with and without search
- ✅ `search_web()` with options
- ✅ `extract_data()` with schema and prompt

#### FirecrawlAdapter
- ✅ Initialization error handling
- ✅ Interface implementation verification
- ✅ `scrape()` method
- ✅ `crawl()` method
- ✅ `map()` method
- ✅ `search()` method
- ✅ `extract()` method
- ✅ Error propagation

#### Conversion Methods
- ✅ `_convert_scrape_result()` from dict and Document object
- ✅ `_convert_crawl_result()` with various data structures
- ✅ `_convert_map_result()`
- ✅ `_convert_search_result()`
- ✅ `_convert_extract_result()`
- ✅ Edge cases with empty/missing data

### Configuration (`test_config.py`)
- ✅ Default configuration values
- ✅ Custom configuration
- ✅ `from_env()` with various environment variables
- ✅ Validation with and without API key
- ✅ Invalid timeout and retries
- ✅ `to_dict()` method
- ✅ Global config functions (`get_config`, `set_config`, `reset_config`)

### Integration Tests (`test_scrape_integration.py`)
- ✅ Basic scraping (requires API key)
- ✅ Scraping with multiple formats
- ✅ Website mapping
- ✅ Web search
- ✅ Data extraction (optional)
- ✅ Error handling with invalid API keys

## Running Tests

### Unit Tests
```bash
# Run all unit tests
pytest src/codomyrmex/scrape/tests/unit/

# Run specific test file
pytest src/codomyrmex/scrape/tests/unit/test_scraper.py

# Run with coverage
pytest src/codomyrmex/scrape/tests/unit/ --cov=codomyrmex.scrape --cov-report=html
```

### Integration Tests
```bash
# Set API key first
export FIRECRAWL_API_KEY="your-api-key"

# Run integration tests
pytest src/codomyrmex/scrape/tests/integration/
```

## Test Requirements

- `pytest>=8.0.0`
- `firecrawl-py>=1.0.0` (optional, for integration tests and some unit tests)

## Notes

- **No Mock Methods**: All tests use real implementations. When external dependencies (like firecrawl-py) are not available, tests are skipped rather than using mocks.
- **Real Data Analysis**: All data processing and conversion logic is tested with real data structures.
- **Test Adapters**: Unit tests use test adapters that implement the BaseScraper interface, not mocks of data processing.
- **Integration Tests**: Require a valid Firecrawl API key for end-to-end testing.
- **Error Cases**: Comprehensively tested with real error propagation.
- **Edge Cases**: Boundary conditions and edge cases are covered with real data.

