import pytest
from load_scores import load_scores


@pytest.fixture
def make_csv(tmp_path):
    """테스트용 CSV 파일을 생성하는 헬퍼 픽스처."""
    def _make(content: str, encoding: str = "utf-8") -> str:
        file_path = tmp_path / "scores.csv"
        file_path.write_text(content, encoding=encoding)
        return str(file_path)
    return _make


# =====================================================================
# 1. 정상 동작 (Normal Cases)
# =====================================================================

def test_valid_rows_and_whitespace_stripping(make_csv):
    """정상적인 데이터 행 및 이름/점수 앞뒤 공백 제거 확인."""
    csv_text = (
        "이름,점수\n"
        "홍길동,85\n"
        "  김철수  ,  92  \n"
        "이영희,0\n"
    )
    path = make_csv(csv_text)
    kept, skipped = load_scores(path)

    assert kept == [("홍길동", 85), ("김철수", 92), ("이영희", 0)]
    assert skipped == []


def test_duplicate_names_are_kept(make_csv):
    """★ 동명이인(같은 이름 중복)이 있을 때 지우지 않고 모두 유지하는지 확인."""
    csv_text = (
        "이름,점수\n"
        "김민수,70\n"
        "박지훈,88\n"
        "김민수,95\n"
    )
    path = make_csv(csv_text)
    kept, skipped = load_scores(path)

    assert kept == [("김민수", 70), ("박지훈", 88), ("김민수", 95)]
    assert skipped == []


def test_utf8_bom_support(make_csv):
    """utf-8-sig(BOM 포함) 파일 정상 처리 확인."""
    csv_text = "이름,점수\n최유리,100\n"
    path = make_csv(csv_text, encoding="utf-8-sig")
    kept, skipped = load_scores(path)

    assert kept == [("최유리", 100)]
    assert skipped == []


# =====================================================================
# 2. 경계값 테스트 (Boundary Cases)
# =====================================================================

@pytest.mark.parametrize(
    "score_str, expected_valid, expected_reason",
    [
        ("-1", False, "점수가 0~100 밖"),   # 하한 바로 아래
        ("0", True, None),                   # 하한 경계값 (유효)
        ("1", True, None),                   # 하한 바로 위
        ("99", True, None),                  # 상한 바로 아래
        ("100", True, None),                 # 상한 경계값 (유효)
        ("101", False, "점수가 0~100 밖"),  # 상한 바로 위
    ],
)
def test_score_boundaries(make_csv, score_str, expected_valid, expected_reason):
    """점수 허용 범위(0~100)의 경계값(-1, 0, 1, 99, 100, 101) 검증."""
    csv_text = f"이름,점수\n테스터,{score_str}\n"
    path = make_csv(csv_text)
    kept, skipped = load_scores(path)

    if expected_valid:
        assert kept == [("테스터", int(score_str))]
        assert skipped == []
    else:
        assert kept == []
        assert skipped == [(2, f"테스터,{score_str}", expected_reason)]


def test_header_only_and_empty_file(make_csv):
    """명세 ②: 헤더만 있는 경우 및 완전히 빈 파일인 경우 ([], []) 반환."""
    # 헤더만 존재
    path_header_only = make_csv("이름,점수\n")
    assert load_scores(path_header_only) == ([], [])

    # 완전히 빈 파일
    path_empty = make_csv("")
    assert load_scores(path_empty) == ([], [])


def test_blank_lines_ignored_without_skip_record_and_preserve_line_no(make_csv):
    """빈 줄은 skipped에 기록되지 않으며, 이후 행의 줄번호(line_no)는 실제 파일 줄번호를 유지."""
    csv_text = (
        "이름,점수\n"    # 1행: 헤더
        "\n"             # 2행: 빈 줄 (무시)
        "홍길동,80\n"    # 3행: 정상
        "\n"             # 4행: 빈 줄 (무시)
        "김철수,150\n"   # 5행: 범위 초과 (line_no == 5 여야 함)
    )
    path = make_csv(csv_text)
    kept, skipped = load_scores(path)

    assert kept == [("홍길동", 80)]
    assert skipped == [(5, "김철수,150", "점수가 0~100 밖")]


# =====================================================================
# 3. 예외 및 건너뛰기 조건 (Exception & Skip Cases)
# =====================================================================

def test_file_not_found_raises_error(tmp_path):
    """명세 ①: 존재하지 않는 파일 경로 전달 시 FileNotFoundError 발생."""
    non_existent = tmp_path / "does_not_exist.csv"
    with pytest.raises(FileNotFoundError):
        load_scores(str(non_existent))


@pytest.mark.parametrize(
    "line_content, expected_reason",
    [
        # 명세 ③: 열 개수가 2가 아님
        ("홍길동", "열 개수가 2가 아님"),
        ("홍길동,80,추가열", "열 개수가 2가 아님"),
        # 명세 ⑥: 이름이 비어 있음 (공백만 있는 경우 포함)
        (",85", "이름이 비어 있음"),
        ("   ,85", "이름이 비어 있음"),
        # 명세 ④: 점수가 비어 있음
        ("홍길동,", "점수가 비어 있음"),
        ("홍길동,   ", "점수가 비어 있음"),
        # 명세 ④: 점수가 정수가 아님
        ("홍길동,85.5", "점수가 정수가 아님"),
        ("홍길동,A+", "점수가 정수가 아님"),
        ("홍길동,팔십", "점수가 정수가 아님"),
        # 명세 ⑤: 점수가 0~100 밖
        ("홍길동,-10", "점수가 0~100 밖"),
        ("홍길동,105", "점수가 0~100 밖"),
    ],
)
def test_invalid_rows_skipped_with_exact_reasons(make_csv, line_content, expected_reason):
    """명세 ③~⑥의 각 오류 케이스별로 정확한 줄번호, 원본줄, 이유가 기록되는지 확인."""
    csv_text = f"이름,점수\n{line_content}\n"
    path = make_csv(csv_text)
    kept, skipped = load_scores(path)

    assert kept == []
    assert skipped == [(2, line_content, expected_reason)]


def test_validation_priority_when_multiple_errors_exist(make_csv):
    """한 줄에 여러 문제가 동시에 있을 때(예: 이름과 점수가 모두 비어 있음) 우선순위 확인."""
    csv_text = (
        "이름,점수\n"
        ",\n"            # 2행: 이름과 점수 모두 비어 있음 -> 이름 검사 우선
        " ,abc,123\n"    # 3행: 열 개수 오류와 이름 공백 동시 발생 -> 열 개수 검사 우선
    )
    path = make_csv(csv_text)
    kept, skipped = load_scores(path)

    assert kept == []
    assert skipped == [
        (2, ",", "이름이 비어 있음"),
        (3, " ,abc,123", "열 개수가 2가 아님"),
    ]


def test_mixed_comprehensive_scenario(make_csv):
    """정상 데이터, 동명이인, 빈 줄, 다양한 오류 줄이 섞여 있는 종합 시나리오."""
    csv_text = (
        "이름,점수\n"          # 1행: 헤더
        "강감찬,90\n"          # 2행: 정상
        "\n"                   # 3행: 빈 줄
        "이순신\n"             # 4행: 열 개수 오류
        "유관순,100\n"         # 5행: 정상
        "강감찬,75\n"          # 6행: 중복 이름
        "   ,50\n"             # 7행: 이름 공백
        "세종대왕,\n"          # 8행: 점수 공백
        "신사임당,95\n"        # 9행: 정상
    )

    path = make_csv(csv_text)
    kept, skipped = load_scores(path)

    assert kept == [
        ("강감찬", 90),
        ("유관순", 100),
        ("강감찬", 75),
        ("신사임당", 95),
    ]

    assert skipped == [
        (4, "이순신", "열 개수가 2가 아님"),
        (7, "   ,50", "이름이 비어 있음"),
        (8, "세종대왕,", "점수가 비어 있음"),
    ]