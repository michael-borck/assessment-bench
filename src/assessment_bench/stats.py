"""Consistency and agreement statistics.

The run-level statistics (mean/median/sample std-dev/CV/reliability) are a port
of the original AssessmentBench Rust aggregation engine — the best-validated
concept in that prototype. Agreement (Pearson/Spearman against human marks) is
new here: it is the bench's core research output. Pure stdlib, no numpy.
"""

from __future__ import annotations

from .models import RunStats


def run_stats(scores: list[float]) -> RunStats | None:
    """Consistency statistics over one arm's repeated scores. None when empty."""
    if not scores:
        return None
    n = len(scores)
    mean = sum(scores) / n
    ordered = sorted(scores)
    median = (
        ordered[n // 2]
        if n % 2
        else (ordered[n // 2 - 1] + ordered[n // 2]) / 2.0
    )
    if n > 1:
        variance = sum((s - mean) ** 2 for s in scores) / (n - 1)
        std_dev = variance**0.5
    else:
        std_dev = 0.0
    cv = std_dev / mean if mean else 0.0
    return RunStats(
        n=n,
        mean=mean,
        median=median,
        std_dev=std_dev,
        coefficient_of_variation=cv,
        min=ordered[0],
        max=ordered[-1],
        reliability=max(0.0, 1.0 - cv),
    )


def pearson(xs: list[float], ys: list[float]) -> float | None:
    """Pearson r. None when undefined (n<2 or zero variance) — never faked as 0."""
    n = len(xs)
    if n != len(ys) or n < 2:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx == 0 or syy == 0:
        return None
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return sxy / (sxx**0.5 * syy**0.5)


def _ranks(values: list[float]) -> list[float]:
    """Average ranks (ties share the mean of their rank positions)."""
    indexed = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i
        while j + 1 < len(indexed) and values[indexed[j + 1]] == values[indexed[i]]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[indexed[k]] = avg_rank
        i = j + 1
    return ranks


def spearman(xs: list[float], ys: list[float]) -> float | None:
    """Spearman rho = Pearson on average ranks. None when undefined."""
    if len(xs) != len(ys) or len(xs) < 2:
        return None
    return pearson(_ranks(xs), _ranks(ys))
