from load_scores import load_scores

def test_normal():
    result = load_scores("scores.csv")
    assert result is not None

def test_score_data():
    scores, skipped = load_scores("scores.csv")

    assert ("김하나", 88) in scores

def test_empty_csv():
    scores, skipped = load_scores("empty.csv")

    assert scores == []
    assert skipped == []

def test_invalid_scores():
    scores, skipped = load_scores("weird.csv")

    assert all(0 <= score <= 100 for name, score in scores)
    assert len(skipped) > 0
import pytest

def test_missing_file():
    with pytest.raises(OSError):
        load_scores("없는파일.csv")
def test_duplicate_names():
    scores, skipped = load_scores("scores.csv")

    assert ("김하나", 88) in scores
    assert ("김하나", 91) in scores