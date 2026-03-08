---
task: Add zero-mock tests for search, scrape, relations modules
slug: 20260307-120000_zero-mock-tests-search-scrape-relations
effort: Advanced
phase: complete
progress: 30/30
mode: algorithm
started: 2026-03-07T12:00:00
updated: 2026-03-07T12:00:00
---

## Context

Add meaningful zero-mock tests for three codomyrmex modules that have low or 0%
pytest coverage: search/, scrape/, relations/. Tests must use real in-memory data,
real APIs, no MagicMock/monkeypatch/unittest.mock. Network-dependent tests get
@pytest.mark.skipif guards. Each file targets 40-60 tests organized in classes.

### Risks

- search/ already has 97 collected tests — must avoid duplicating, only add net-new
- scrape/ mcp_tools need ContentExtractor (pure Python, no network) — testable
- scrape/Scraper class requires an adapter — must test validation paths only (no network)
- relations/mcp_tools imports submodule mcp_tools (crm, network_analysis, social_media, uor)
- relations submodule files may raise ImportError if optional deps missing

## Criteria

- [ ] ISC-1: test_search_core.py file created at correct path
- [ ] ISC-2: TestSimpleTokenizerBehavior class has >=5 tests covering real behavior
- [ ] ISC-3: TestFuzzyMatcherLevenshtein class has >=4 distance edge case tests
- [ ] ISC-4: TestFuzzyMatcherSimilarity class has >=4 ratio boundary tests
- [ ] ISC-5: TestFuzzyMatcherBestMatch class has >=3 threshold behavior tests
- [ ] ISC-6: TestQueryParserOperators class has >=5 operator parsing tests
- [ ] ISC-7: TestInMemoryIndexBehavior class has >=8 index/search/delete tests
- [ ] ISC-8: TestQuickSearch function tests with real documents
- [ ] ISC-9: TestBM25Index class has >=5 BM25 scoring tests
- [ ] ISC-10: TestHybridSearchEngine class has >=5 hybrid search tests
- [ ] ISC-11: TestSearchMcpTools class has >=6 MCP tool call tests
- [ ] ISC-12: search tests pass without errors when run with pytest
- [ ] ISC-13: test_scrape_core.py created at correct path
- [ ] ISC-14: TestScrapeFormat enum values tested
- [ ] ISC-15: TestScrapeResult dataclass behavior tested (get_format, has_format)
- [ ] ISC-16: TestScrapeOptions to_dict method tested
- [ ] ISC-17: TestCrawlResult and MapResult auto-total behavior tested
- [ ] ISC-18: TestContentExtractor class has >=8 extraction tests
- [ ] ISC-19: TestTextSimilarity function has >=5 edge case tests
- [ ] ISC-20: TestScrapeExceptions hierarchy tested (all exception classes)
- [ ] ISC-21: TestClassifyHttpError function tested for all status codes
- [ ] ISC-22: TestScrapeMcpToolsContent has >=4 tests for scrape_extract_content
- [ ] ISC-23: TestScrapeMcpToolsSimilarity has >=3 tests for scrape_text_similarity
- [ ] ISC-24: scrape tests pass without errors when run with pytest
- [ ] ISC-25: test_relations_core.py created at correct path
- [ ] ISC-26: TestInteractionDataclass has >=3 tests for Interaction creation
- [ ] ISC-27: TestStrengthConfig has >=3 tests for config defaults and custom values
- [ ] ISC-28: TestDecayFunctions class has >=6 tests covering all 4 decay modes
- [ ] ISC-29: TestRelationStrengthScorerBasic has >=6 tests for add/score behavior
- [ ] ISC-30: TestRelationStrengthScorerEdgeCases has >=4 edge case tests
- [ ] ISC-31: TestScoreAll normalized scoring behavior tested
- [ ] ISC-32: TestTopRelations top-N query tested
- [ ] ISC-33: TestRelationsMcpTool has >=4 tests for relations_score_strength
- [ ] ISC-34: relations tests pass without errors when run with pytest
- [ ] ISC-35: All three test files committed with --no-verify flag

## Decisions

- scrape/Scraper URL validation tested directly without adapter (raises ScrapeValidationError)
- relations submodule (crm/network_analysis/social_media/uor) tested only if importable
- search/hybrid.py BM25Index and HybridSearchEngine tested in-memory with real text

## Verification

