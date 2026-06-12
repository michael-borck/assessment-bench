"""Stats: the ported Rust aggregation math + the new agreement correlations."""

import pytest

from assessment_bench.stats import pearson, run_stats, spearman


def test_run_stats_basic():
    s = run_stats([80.0, 85.0, 90.0])
    assert s.n == 3
    assert s.mean == pytest.approx(85.0)
    assert s.median == pytest.approx(85.0)
    assert s.std_dev == pytest.approx(5.0)  # sample std-dev (n-1)
    assert s.coefficient_of_variation == pytest.approx(5.0 / 85.0)
    assert s.min == 80.0 and s.max == 90.0
    assert s.reliability == pytest.approx(1.0 - 5.0 / 85.0)


def test_run_stats_even_median_and_single():
    assert run_stats([1.0, 2.0, 3.0, 4.0]).median == pytest.approx(2.5)
    single = run_stats([70.0])
    assert single.std_dev == 0.0 and single.reliability == 1.0
    assert run_stats([]) is None


def test_pearson_perfect_and_inverse():
    assert pearson([1, 2, 3], [10, 20, 30]) == pytest.approx(1.0)
    assert pearson([1, 2, 3], [30, 20, 10]) == pytest.approx(-1.0)


def test_pearson_undefined_not_faked():
    assert pearson([1, 1, 1], [1, 2, 3]) is None  # zero variance
    assert pearson([1], [1]) is None  # n < 2


def test_spearman_monotonic_nonlinear():
    # Monotonic but nonlinear: rho is 1 even where r is not.
    xs = [1.0, 2.0, 3.0, 4.0]
    ys = [1.0, 10.0, 100.0, 1000.0]
    assert spearman(xs, ys) == pytest.approx(1.0)


def test_spearman_ties_average_ranks():
    assert spearman([1.0, 1.0, 2.0], [1.0, 1.0, 2.0]) == pytest.approx(1.0)
