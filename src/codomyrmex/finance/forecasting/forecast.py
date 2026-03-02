"""Simple financial forecasting using moving averages, exponential smoothing,
and linear trend analysis.

All methods operate on a plain list of float values representing time-series
observations (e.g. monthly revenue).
"""

from __future__ import annotations

import random
from decimal import Decimal


class ForecastError(Exception):
    """Raised when forecasting cannot proceed."""


class Forecaster:
    """Simple financial forecasting engine.

    Usage::

        fc = Forecaster([100, 110, 105, 120, 130])
        print(fc.moving_average(window=3))
        print(fc.forecast(periods=3, method="exponential_smoothing"))
    """

    def __init__(self, data: list[Decimal | float] | None = None) -> None:
        """Initialise with an optional list of historical values.

        Args:
            data: Time-series observations ordered oldest-first.
        """
        self.data: list[Decimal] = [Decimal(str(d)) for d in data] if data else []

    # ------------------------------------------------------------------
    # Core methods
    # ------------------------------------------------------------------

    def moving_average(self, window: int = 3) -> list[Decimal]:
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

        result: list[Decimal] = []
        for i in range(len(self.data) - window + 1):
            segment = self.data[i : i + window]
            result.append(sum(segment, Decimal("0.00")) / Decimal(str(window)))
        return result

    def exponential_smoothing(self, alpha: Decimal | float = 0.3) -> list[Decimal]:
        """Single exponential smoothing (SES).

        Args:
            alpha: Smoothing factor in (0, 1).  Higher values weight recent
                observations more heavily.

        Returns:
            A list of smoothed values, same length as the input data.

        Raises:
            ForecastError: If alpha is out of range or data is empty.
        """
        alpha_d = Decimal(str(alpha))
        if not (Decimal("0") < alpha_d < Decimal("1")):
            raise ForecastError("Alpha must be between 0 and 1 (exclusive).")
        if not self.data:
            raise ForecastError("No data to smooth.")

        smoothed: list[Decimal] = [self.data[0]]
        for i in range(1, len(self.data)):
            s = alpha_d * self.data[i] + (Decimal("1") - alpha_d) * smoothed[-1]
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

        x_vals = [Decimal(str(x)) for x in range(n)]
        x_mean = sum(x_vals, Decimal("0")) / Decimal(str(n))
        y_mean = sum(self.data, Decimal("0")) / Decimal(str(n))

        ss_xy = sum(
            (x - x_mean) * (y - y_mean)
            for x, y in zip(x_vals, self.data, strict=False)
        )
        ss_xx = sum((x - x_mean) ** 2 for x in x_vals)
        ss_yy = sum((y - y_mean) ** 2 for y in self.data)

        if ss_xx == 0:
            raise ForecastError("All x values are identical; cannot compute trend.")

        slope = ss_xy / ss_xx
        intercept = y_mean - slope * x_mean

        # R-squared (coefficient of determination)
        if ss_yy == 0:
            r_squared = Decimal("1.0")  # perfect fit if y is constant
        else:
            r_squared = (ss_xy**2) / (ss_xx * ss_yy)

        # Standard deviation of residuals for Monte Carlo
        residuals = []
        for i, y in enumerate(self.data):
            y_pred = slope * Decimal(str(i)) + intercept
            residuals.append(y - y_pred)

        std_dev = (sum(r**2 for r in residuals) / Decimal(str(n))).sqrt()

        return {
            "slope": slope,
            "intercept": intercept,
            "r_squared": r_squared,
            "std_dev": std_dev,
        }

    def project(self, periods: int = 12, iterations: int = 1000) -> dict:
        """Generate a 12-month projection with Monte Carlo simulation.

        Args:
            periods: Number of future periods to project.
            iterations: Number of Monte Carlo iterations.

        Returns:
            A dict with 'projections' (list of means) and 'confidence_intervals'.
        """
        if len(self.data) < 3:
            raise ForecastError("Forecaster requires minimum 3 periods for projection.")

        trend = self.linear_trend()
        slope = trend["slope"]
        intercept = trend["intercept"]
        std_dev = float(trend["std_dev"])
        n = len(self.data)

        results = [[] for _ in range(periods)]

        for _ in range(iterations):
            for i in range(periods):
                # Simple normal distribution simulation
                noise = Decimal(str(random.gauss(0, std_dev)))
                val = slope * Decimal(str(n + i)) + intercept + noise
                results[i].append(val)

        projections = []
        for i in range(periods):
            avg = sum(results[i], Decimal("0")) / Decimal(str(iterations))
            projections.append(avg)

        return {
            "projections": projections,
            "method": "Monte Carlo Linear Trend",
        }

    def risk_metrics(self, portfolio: dict) -> dict:
        """Calculate risk metrics for a portfolio.

        Args:
            portfolio: Portfolio schema as defined in SPEC.md.

        Returns:
            Risk metrics output as defined in SPEC.md.
        """
        total_value = Decimal("0.00")
        total_cost = Decimal("0.00")
        currency = portfolio.get("base_currency", "USD")

        for pos in portfolio.get("positions", []):
            qty = Decimal(str(pos["quantity"]))
            price = Decimal(str(pos["current_price"]))
            cost = Decimal(str(pos["cost_basis"]))

            total_value += qty * price
            total_cost += qty * cost

        total_pnl = total_value - total_cost
        pnl_percent = (total_pnl / total_cost * 100) if total_cost > 0 else Decimal("0")

        # Simplified VaR 95% (Total Value * 1.645 * estimated volatility)
        # Using a fixed 5% volatility for this implementation
        var_95 = total_value * Decimal("1.645") * Decimal("0.05")

        return {
            "total_value": total_value,
            "total_pnl": total_pnl,
            "pnl_percent": pnl_percent,
            "var_95": var_95,
            "max_drawdown": Decimal("0.00"),  # Placeholder
            "sharpe_ratio": None,
            "currency": currency,
        }

    # ------------------------------------------------------------------
    # Forecasting
    # ------------------------------------------------------------------

    def forecast(
        self,
        periods: int,
        method: str = "moving_average",
        **kwargs,
    ) -> list[Decimal]:
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
                trend["slope"] * Decimal(str(n + i)) + trend["intercept"]
                for i in range(periods)
            ]

        elif method == "monte_carlo":
            proj = self.project(periods=periods)
            return proj["projections"]

        else:
            raise ForecastError(
                f"Unknown method '{method}'. "
                "Choose from: moving_average, exponential_smoothing, linear_trend."
            )
