---
task: Add zero-mock tests for 5 untested modules
slug: 20260307-120000_coverage-push-5-modules
effort: Advanced
phase: execute
progress: 0/28
mode: ALGORITHM
started: 2026-03-07T12:00:00Z
updated: 2026-03-07T12:00:00Z
---

## Context

Push test coverage for codomyrmex Python codebase. Current test_health: 21.4%.
Target: add meaningful zero-mock tests for 5+ currently untested modules.
Modules chosen: finance, market, deployment, dark, and email (generics/exceptions).

Zero-mock policy: no MagicMock, monkeypatch, unittest.mock.
External deps: use @pytest.mark.skipif guards.
All assertions must test real behavior (not assert True).

### Risks
- Import errors if module deps not installed (skip guards needed)
- finance/payroll depends on taxes — must test integration correctly
- deployment strategies use callables — real lambdas, not mocks
- dark module needs PyMuPDF for PDF tests — must skipif not installed
- email module likely needs AGENTMAIL_API_KEY for real calls

## Criteria

- [ ] ISC-1: finance/ledger tests file exists with 10+ tests
- [ ] ISC-2: Ledger creates accounts with correct type and name format
- [ ] ISC-3: Ledger rejects account names without colon separator
- [ ] ISC-4: Ledger posts balanced transactions and updates balances
- [ ] ISC-5: Ledger rejects unbalanced transactions with LedgerError
- [ ] ISC-6: Ledger get_balance_sheet returns assets/liabilities/equity keys
- [ ] ISC-7: Ledger get_income_statement returns revenue/expenses/net_income
- [ ] ISC-8: Ledger trial_balance reports balanced=True after valid transactions
- [ ] ISC-9: TaxCalculator computes US progressive tax with correct bracket structure
- [ ] ISC-10: TaxCalculator raises TaxError for negative income
- [ ] ISC-11: TaxCalculator apply_deductions reduces taxable income correctly
- [ ] ISC-12: TaxCalculator supports UK jurisdiction
- [ ] ISC-13: Forecaster moving_average returns correct values for known dataset
- [ ] ISC-14: Forecaster exponential_smoothing raises on invalid alpha
- [ ] ISC-15: Forecaster forecast returns correct number of future periods
- [ ] ISC-16: PayrollProcessor calculate_pay returns net_pay < gross
- [ ] ISC-17: PayrollProcessor generate_pay_stub populates PayStub correctly
- [ ] ISC-18: market/auction tests file exists with 10+ tests
- [ ] ISC-19: ReverseAuction creates auction request with OPEN status
- [ ] ISC-20: ReverseAuction place_bid rejects amount over max_price
- [ ] ISC-21: ReverseAuction sorts bids by lowest amount first
- [ ] ISC-22: ReverseAuction close_auction blocks unauthorized requester
- [ ] ISC-23: DemandAggregator register_interest accumulates entries
- [ ] ISC-24: DemandAggregator get_stats returns correct CategoryStats
- [ ] ISC-25: deployment tests file exists with 10+ tests
- [ ] ISC-26: RollingDeployment deploys targets with real callable
- [ ] ISC-27: BlueGreenDeployment tracks slot metadata correctly
- [ ] ISC-28: CanaryDeployment aborts on low success rate

## Decisions

## Verification
