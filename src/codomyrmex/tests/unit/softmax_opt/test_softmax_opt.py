import numpy as np
import pytest

from codomyrmex.softmax_opt import log_softmax, online_softmax, softmax


class TestSoftmax:
    @pytest.mark.unit
    def test_output_sums_to_one(self) -> None:
        x = np.array([1.0, 2.0, 3.0, 4.0])
        out = softmax(x)
        assert abs(np.sum(out) - 1.0) < 1e-6

    @pytest.mark.unit
    def test_all_positive(self) -> None:
        x = np.array([-5.0, 0.0, 5.0, 100.0])
        out = softmax(x)
        assert np.all(out > 0)

    @pytest.mark.unit
    def test_numerically_stable_large_values(self) -> None:
        """Should not overflow/underflow for large inputs."""
        x = np.array([1000.0, 1001.0, 999.0])
        out = softmax(x)
        assert not np.any(np.isnan(out))
        assert not np.any(np.isinf(out))
        assert abs(np.sum(out) - 1.0) < 1e-5

    @pytest.mark.unit
    def test_temperature_scaling(self) -> None:
        x = np.array([1.0, 2.0, 3.0])
        out_hot = softmax(x, temperature=0.1)  # peaked
        out_cold = softmax(x, temperature=10.0)  # uniform
        # Low temperature -> max probability higher
        assert np.max(out_hot) > np.max(out_cold)

    @pytest.mark.unit
    def test_2d_along_axis(self) -> None:
        x = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
        out = softmax(x, axis=1)
        row_sums = np.sum(out, axis=1)
        np.testing.assert_allclose(row_sums, [1.0, 1.0], atol=1e-6)


class TestLogSoftmax:
    @pytest.mark.unit
    def test_log_softmax_matches_log_of_softmax(self) -> None:
        x = np.array([1.0, 2.0, 3.0, 0.5])
        log_sm = log_softmax(x)
        sm_then_log = np.log(softmax(x))
        np.testing.assert_allclose(log_sm, sm_then_log, atol=1e-5)


class TestOnlineSoftmax:
    @pytest.mark.unit
    def test_online_matches_standard(self) -> None:
        x = np.array([0.5, 1.0, 2.0, 0.1, -0.5])
        standard = softmax(x)
        online = online_softmax(x)
        np.testing.assert_allclose(online, standard, atol=1e-6)

    @pytest.mark.unit
    def test_online_sums_to_one(self) -> None:
        x = np.random.randn(10)
        out = online_softmax(x)
        assert abs(np.sum(out) - 1.0) < 1e-6
