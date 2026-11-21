"""명세서 기반 AI 테스트 B.

근거: 10주차 실습 보고서의 여섯 칸 점검 기준 및 v4 처리 단계.
실제 load_scores.py 구현 코드는 제공받지 않은 상태에서 작성했다.
"""

import csv
import pytest
from load_scores import load_scores


@pytest.fixture
def csv_file(tmp_path):
    def create(rows, header=("name", "score")):
        path = tmp_path / "sample.csv"
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)
        return str(path)
    return create


def test_normal_scores(csv_file):
    path = csv_file([["Kim", "88"], ["Lee", "95"]])
    scores, skipped = load_scores(path)
    assert scores == [("Kim", 88), ("Lee", 95)]
    assert skipped == []


def test_score_boundaries(csv_file):
    path = csv_file([["Low", "0"], ["High", "100"], ["Below", "-1"], ["Above", "101"]])
    scores, skipped = load_scores(path)
    assert scores == [("Low", 0), ("High", 100)]
    assert len(skipped) == 2


def test_invalid_and_missing_scores(csv_file):
    path = csv_file([["Missing", ""], ["Text", "abc"], ["Fraction", "3.5"], ["Valid", "72"]])
    scores, skipped = load_scores(path)
    assert scores == [("Valid", 72)]
    assert len(skipped) == 3


def test_missing_name_and_column_count(csv_file):
    path = csv_file([["", "85"], ["OnlyName"], ["Too", "80", "extra"], ["Good", "90"]])
    scores, skipped = load_scores(path)
    assert scores == [("Good", 90)]
    assert len(skipped) == 3


def test_duplicate_names_preserved(csv_file):
    path = csv_file([["Kim", "70"], ["Kim", "90"]])
    scores, skipped = load_scores(path)
    assert scores == [("Kim", 70), ("Kim", 90)]
    assert skipped == []


def test_skipped_records_include_line_reason_original(csv_file):
    path = csv_file([["Good", "80"], ["Bad", "105"]])
    scores, skipped = load_scores(path)
    assert scores == [("Good", 80)]
    assert len(skipped) == 1
    record = skipped[0]
    assert isinstance(record, (tuple, list)) and len(record) == 3
    line_number, reason, original_row = record
    assert line_number == 3
    assert isinstance(reason, str) and reason.strip()
    assert original_row is not None


def test_header_only(csv_file):
    path = csv_file([])
    assert load_scores(path) == ([], [])


def test_invalid_header_rejected(csv_file):
    path = csv_file([["Kim", "80"]], header=("person", "points"))
    with pytest.raises(ValueError):
        load_scores(path)


def test_missing_file_raises_oserror(tmp_path):
    path = tmp_path / "does_not_exist.csv"
    with pytest.raises(OSError):
        load_scores(str(path))