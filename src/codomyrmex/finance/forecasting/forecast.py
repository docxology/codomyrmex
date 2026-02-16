"""Simple financial forecasting using moving averages, exponential smoothing,
and linear trend analysis.

All methods operate on a plain list of float values representing time-series
observations (e.g. monthly revenue).
"""

from __future__ import annotations

import math
from typing import Optional


class ForecastError(Exception):
    """Raised when forecasting cannot proceed."""


class Forecaster:
    """Simple financial forecasting engine.

    Usage::

        fc = Forecaster([100, 110, 105, 120, 130])
        print(fc.moving_average(window=3))
        print(fc.forecast(periods=3, method="exponential_smoothing"))
    """

    def __init__(self, data: Optional[list[float]] = None) -> None:
        """Initialise with an optional list of historical values.

        Args:
            data: Time-series observations ordered oldest-first.
        """
        self.data: list[float] = list(data) if data else []

    # ------------------------------------------------------------------
    # Core methods
    # ------------------------------------------------------------------

    def moving_average(self, window: int = 3) -> list[float]:
        """Compute the simple moving average over the data.

        Args:
            window: Number of periods to average over.

        Returns:
            A list of moving-average values (shorter than input by
            ``window - 1`` elements).

        Raises:
            ForecastError: If there is not enough data for the given window.
        """
        if window < 1:
            raise ForecastError("Window must be >= 1.")
        if len(self.data) < window:
            raise ForecastError(
                f"Need at least {window} data points; got {len(self.data)}."
            )

        result: list[float] = []
        for i in range(len(self.data) - window + 1):
            segment = self.data[i : i + window]
            result.append(sum(segment) / window)
        return result

    def exponential_smoothing(self, alpha: float = 0.3) -> list[float]:
        """Single exponential smoothing (SES).

        Args:
            alpha: Smoothing factor in (0, 1).  Higher values weight recent
                observations more heavily.

        Returns:
            A list of smoothed values, same length as the input data.

        Raises:
            ForecastError: If alpha is out of range or data is empty.
        """
        if not (0 < alpha < 1):
            raise ForecastError("Alpha must be between 0 and 1 (exclusive).")
        if not self.data:
            raise ForecastError("No data to smooth.")

        smoothed: list[float] = [self.data[0]]
        for i in range(1, len(self.data)):
            s = alpha * self.data[i] + (1 - alpha) * smoothed[-1]
            smoothed.append(s)
        return smoothed

    def linear_trend(self) -> dict:
        """Fit a simple linear regression y = slope * x + intercept.

        Uses ordinary least squares on indices 0..n-1 as the independent
        variable.

        Returns:
            A dict with ``slope``, ``intercept``, and ``r_squared``.

        Raises:
            ForecastError: If fewer than 2 data points are available.
        """
        n = len(self.data)
        if n < 2:
            raise ForecastError("Need at least 2 data points for linear trend.")

        x_vals = list(range(n))
        x_mean = sum(x_vals) / n
        y_mean = sum(self.data) / n

        ss_xy = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_vals, self.data))
        ss_xx = sum((x - x_mean) ** 2 for x in x_vals)
        ss_yy = sum((y - y_mean) ** 2 for y in self.data)

        if ss_xx == 0:
            raise ForecastError("All x values are identical; cannot compute trend.")

        slope = ss_xy / ss_xx
        intercept = y_mean - slope * x_mean

        # R-squared (coefficient of determination)
        if ss_yy == 0:
            r_squared = 1.0  # perfect fit if y is constant
        else:
            r_squared = (ss_xy ** 2) / (ss_xx * ss_yy)

        return {
            "slope": slope,
            "intercept": intercept,
            "r_squared": r_squared,
        }

    # ------------------------------------------------------------------
    # Forecasting
    # ------------------------------------------------------------------

    def forecast(
        self,
        periods: int,
        method: str = "moving_average",
        **kwargs,
    ) -> list[float]:
        """Generate future forecasted values.

        Supported methods:
            - ``"moving_average"`` -- projects the last moving-average value
              forward.  Accepts ``window`` kwarg (default 3).
            - ``"exponential_smoothing"`` -- projects the last smoothed value
              forward.  Accepts ``alpha`` kwarg (default 0.3).
            - ``"linear_trend"`` -- extrapolates the fitted line.

        Args:
            periods: Number of future periods to forecast.
            method: Forecasting algorithm name.
            **kwargs: Additional parameters forwarded to the underlying method.

        Returns:
            A list of ``periods`` forecasted values.

        Raises:
            ForecastError: On invalid method or insufficient data.
        """
        if periods < 1:
            raise ForecastError("periods must be >= 1.")

        if method == "moving_average":
            window = kwargs.get("window", 3)
            ma = self.moving_average(window)
            last_value = ma[-1]
            return [last_value] * periods

        elif method == "exponential_smoothing":
            alpha = kwargs.get("alpha", 0.3)
            smoothed = self.exponential_smoothing(alpha)
            last_value = smoothed[-1]
            return [last_value] * periods

        elif method == "linear_trend":
            trend = self.linear_trend()
            n = len(self.data)
            return [
                trend["slope"] * (n + i) + trend["intercept"]
                for i in range(periods)
            ]

        else:
            raise ForecastError(
                f"Unknown method '{method}'. "
                "Choose from: moving_average, exponential_smoothing, linear_trend."
            )
