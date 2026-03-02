# Codomyrmex Agents -- src/codomyrmex/finance/forecasting

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides simple financial time-series forecasting using moving averages, single exponential smoothing, and linear trend analysis. All methods operate on plain lists of float values representing sequential observations (e.g., monthly revenue).

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `forecast.py` | `ForecastError` | Exception raised when forecasting cannot proceed (insufficient data, invalid parameters) |
| `forecast.py` | `Forecaster` | Forecasting engine with moving average, exponential smoothing, linear trend, and multi-period projection |
| `forecast.py` | `Forecaster.moving_average` | Computes simple moving average over a configurable window |
| `forecast.py` | `Forecaster.exponential_smoothing` | Single exponential smoothing (SES) with configurable alpha |
| `forecast.py` | `Forecaster.linear_trend` | Ordinary least squares regression returning slope, intercept, and R-squared |
| `forecast.py` | `Forecaster.forecast` | Generates N future values using any of the three methods |

## Operating Contracts

- `Forecaster` accepts an optional `data` list at construction; data must be ordered oldest-first.
- `moving_average` requires `window >= 1` and at least `window` data points; raises `ForecastError` otherwise.
- `exponential_smoothing` requires `0 < alpha < 1` and non-empty data.
- `linear_trend` requires at least 2 data points and returns `slope`, `intercept`, and `r_squared`.
- `forecast` dispatches to the specified method and projects values forward; raises `ForecastError` for unknown methods.
- No external dependencies -- pure Python implementation using standard math.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: Python stdlib only (no external packages)
- **Used by**: Financial planning modules, dashboard data providers

## Navigation

- **Parent**: [../AGENTS.md](../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
