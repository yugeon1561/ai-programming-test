# CSV 성적 검증 프로그램

## ① 무엇을 하나요 (What)

CSV 파일에서 학생 이름과 점수를 읽어 정상적인 성적만 저장하고, 잘못된 데이터는 제외하면서 오류 내용을 기록하는 프로그램입니다.

## ② 왜 만들었나요 (Why)

실제 성적 파일에는 점수가 비어 있거나 0~100점을 벗어나는 값, 중복된 이름 등이 포함될 수 있습니다. 이런 데이터를 그대로 처리하면 잘못된 성적이 저장될 수 있기 때문에 정상 데이터와 오류 데이터를 구분하는 프로그램이 필요하다고 생각했습니다.

## ③ 어떻게 쓰나요 (How)

Python이 설치된 상태에서 VS Code로 프로젝트 폴더를 열고 터미널에 다음 명령어를 입력합니다.

```bash
# 테스트 도구 설치
py -m pip install pytest pytest-cov

# 프로그램 실행 예시
py -c "from load_scores import load_scores; print(load_scores('scores.csv'))"
```

`load_scores(path)` 함수는 정상 성적 목록과 제외된 행의 기록을 함께 반환합니다.

## ④ 어떻게 테스트하나요

pytest를 사용하여 직접 작성한 테스트와 AI가 생성한 테스트를 실행했습니다.

```bash
# 직접 작성한 테스트
py -m pytest test_load_scores.py -v

# AI 테스트 A
py -m pytest test_ai_A.py --cov=load_scores --cov-report=term-missing -q

# AI 테스트 B
py -m pytest test_ai_B.py --cov=load_scores --cov-report=term-missing -q
```

실제 실행 결과:

```text
직접 작성한 테스트
6 passed

AI 테스트 A
25 passed
TOTAL 45 9 80%

AI 테스트 B
1 failed, 8 passed
TOTAL 45 10 78%
```

AI 테스트 B에서는 잘못된 CSV 헤더를 입력했을 때 `ValueError`가 발생하는지 확인하는 테스트가 실패했습니다.

이번 실습에서는 AI에게 실제 코드를 제공한 A가 명세서만 제공한 B보다 테스트 통과율과 코드 커버리지에서 더 높은 결과를 보였습니다. 다만 테스트 개수가 서로 다르므로 코드 제공 여부만으로 차이가 발생했다고 단정할 수는 없습니다.

## ⑤ 파일 구성

| 파일 | 하는 일 |
|---|---|
| `load_scores.py` | CSV 성적을 읽고 정상 데이터와 오류 기록을 반환하는 프로그램 |
| `scores.csv` | 정상 및 일부 오류 데이터가 포함된 성적 파일 |
| `empty.csv` | 빈 CSV 테스트용 파일 |
| `weird.csv` | 잘못된 성적 데이터 테스트용 파일 |
| `test_load_scores.py` | 직접 작성한 pytest 테스트 6개 |
| `test_ai_A.py` | AI에게 실제 코드를 제공하여 생성한 테스트 |
| `test_ai_B.py` | AI에게 명세서만 제공하여 생성한 테스트 |
| `bug3_logic.py` | 논리 오류 실습용 코드 |
| `prompts.txt` | AI 테스트 A/B 생성에 사용한 프롬프트 |
| `README.md` | 프로그램 설명과 실행 및 테스트 방법 |
| `.gitignore` | Git에서 제외할 파일과 폴더 설정 |

## ⑥ 만든 사람 · AI를 어디에 썼는지

- **만든 사람:** 김유건 / 2026100250 / 한국기술교육대학교 기계공학부
- **AI를 쓴 곳:** CSV 성적 처리 코드 작성 및 검토, pytest 테스트 코드 생성, 테스트 A/B 비교와 README 작성 보조
- **내가 직접 판단한 것:** 성적 검증에 필요한 조건을 정하고, 실제 테스트를 실행하여 정상 작동 여부를 확인했습니다. 또한 테스트 실패 원인과 커버리지 결과를 비교하여 프로그램의 검증 수준을 평가했습니다.

## 라이선스

MIT License (LICENSE 파일 참고)