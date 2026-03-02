# Financial Forecasting -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Simple financial time-series forecasting engine supporting moving averages, single exponential smoothing (SES), and linear trend analysis via ordinary least squares. All methods operate on plain `list[float]` inputs representing sequential observations.

## Architecture

Single-class design (`Forecaster`) with stateless computation methods. The `forecast` method dispatches to the appropriate algorithm by name and projects values forward. No external dependencies -- pure Python using standard math.

## Key Classes

### `Forecaster`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `data: list[float] \| None` | -- | Initialize with optional historical time-series data |
| `moving_average` | `window: int = 3` | `list[float]` | Simple moving average; output is shorter by `window - 1` |
| `exponential_smoothing` | `alpha: float = 0.3` | `list[float]` | Single exponential smoothing; same length as input |
| `linear_trend` | -- | `dict` | OLS regression returning `slope`, `intercept`, `r_squared` |
| `forecast` | `periods: int, method: str, **kwargs` | `list[float]` | Project N future values using the specified method |

### `ForecastError`

Exception raised when forecasting cannot proceed (insufficient data, invalid parameters, unknown method).

## Forecast Methods

| Method Name | Projection Approach | Required Data |
|-------------|-------------------|---------------|
| `moving_average` | Repeats the last moving-average value | At least `window` points |
| `exponential_smoothing` | Repeats the last smoothed value | At least 1 point |
| `linear_trend` | Extrapolates the fitted line (`slope * (n+i) + intercept`) | At least 2 points |

## Dependencies

- **Internal**: None
- **External**: None (Python stdlib only)

## Constraints

- `moving_average` requires `window >= 1` and `len(data) >= window`.
- `exponential_smoothing` requires `0 < alpha < 1` and non-empty data.
- `linear_trend` requires at least 2 data points; raises `ForecastError` if all x-values are identical.
- `forecast` requires `periods >= 1`.
- R-squared is 1.0 when y is constant (perfect fit by definition).
- Zero-mock: real computations only, `NotImplementedError` for unimplemented paths.

## Error Handling

- All validation failures raise `ForecastError` with descriptive messages.
- All errors logged before propagation.
