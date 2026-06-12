"""Score extraction — the riskiest parsing in the bench (the Rust prototype never tested its)."""

import pytest

from assessment_bench.arms import extract_score, grade_prompt


def test_strict_score_line():
    score, _ = extract_score("Good work overall.\nSCORE: 78/100", 100.0)
    assert score == pytest.approx(78.0)


def test_last_score_line_wins():
    text = "If perfect this would be SCORE: 100/100, but...\nSCORE: 62.5/100"
    score, _ = extract_score(text, 100.0)
    assert score == pytest.approx(62.5)


def test_scaled_to_max_score():
    score, _ = extract_score("SCORE: 7/10", 100.0)
    assert score == pytest.approx(70.0)


def test_fallback_out_of_phrasing():
    score, _ = extract_score("I would award 41 out of 50 for this.", 100.0)
    assert score == pytest.approx(82.0)


def test_no_score_returns_none():
    score, _ = extract_score("This is thoughtful work with clear structure.", 100.0)
    assert score is None


def test_grade_prompt_carries_parts():
    p = grade_prompt("RUB", "SUB", 50.0)
    assert "RUB" in p and "SUB" in p and "SCORE: x/50" in p
