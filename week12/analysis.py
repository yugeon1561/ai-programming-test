import pandas as pd


def 정제(df):
    df = df.copy()
    print("시작:", len(df))

    df = df.dropna(subset=["점수"])
    print("결측값 제거:", len(df))

    df = df.drop_duplicates().copy()
    print("중복 제거:", len(df))

    df["반"] = df["반"].str.strip()
    df["과목"] = df["과목"].str.strip()
    print("공백 제거:", len(df))

    df = df[df["점수"].between(0, 100)].copy()
    print("이상치 제거:", len(df))

    return df


def 반별평균(df):
    return df.groupby("반")["점수"].mean()


def 분석(df):
    print("\n=== 수학 데이터 개수 ===")
    print(len(df[df["과목"] == "수학"]))

    print("\n=== 반별 평균 ===")
    print(반별평균(df).round(2))

    print("\n=== 반별 과목 평균 및 개수 ===")
    print(df.groupby(["반", "과목"])["점수"]
          .agg(["count", "mean"]).round(2))

    print("\n=== 반별 통계 ===")
    print(df.groupby("반")["점수"]
          .agg(["count", "mean", "median", "max"])
          .round(2))

    print("\n=== 합계 검증 ===")
    print(df["점수"].sum())
    print(df.groupby("반")["점수"].sum().sum())

    print("\n=== 행 수 검증 ===")
    print(len(df))
    print(df.groupby("반")["점수"].count().sum())


if __name__ == "__main__":
    df = pd.read_csv("scores_2026.csv",
                     dtype={"학번": str})
    cleaned = 정제(df)
    분석(cleaned)