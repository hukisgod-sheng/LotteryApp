import numpy as np
import pandas as pd

from core.constants import BLUE_MAX, BLUE_MIN, RED_MAX, RED_MIN
from core.history import get_red_columns


def _chronological(df: pd.DataFrame) -> pd.DataFrame:
    return df.sort_values("期号", ascending=True).reset_index(drop=True)


def build_omission_timeline(df: pd.DataFrame, ball_type: str = "red") -> pd.DataFrame:
    """逐期遗漏走势，模仿官网遗漏曲线数据。"""
    df = _chronological(df)
    red_cols = get_red_columns()
    lo, hi = (RED_MIN, RED_MAX) if ball_type == "red" else (BLUE_MIN, BLUE_MAX)
    omit = {n: 0 for n in range(lo, hi + 1)}
    rows: list[dict] = []

    for _, row in df.iterrows():
        if ball_type == "red":
            drawn = {int(row[c]) for c in red_cols}
        else:
            drawn = {int(row["蓝球"])}

        for n in range(lo, hi + 1):
            omit[n] = 0 if n in drawn else omit[n] + 1
            rows.append({"期号": str(row["期号"]), "号码": n, "遗漏": omit[n]})

    return pd.DataFrame(rows)


def build_metric_timeline(df: pd.DataFrame) -> pd.DataFrame:
    """和值、跨度、奇数个数等指标走势。"""
    df = _chronological(df)
    red_cols = get_red_columns()
    rows: list[dict] = []

    for _, row in df.iterrows():
        reds = [int(row[c]) for c in red_cols]
        rows.append(
            {
                "期号": str(row["期号"]),
                "和值": sum(reds),
                "跨度": max(reds) - min(reds),
                "奇数个数": sum(1 for n in reds if n % 2),
                "蓝球": int(row["蓝球"]),
            }
        )
    return pd.DataFrame(rows)


def build_distribution_matrix(df: pd.DataFrame, ball_type: str = "red") -> pd.DataFrame:
    """号码分布矩阵：行=期号，列=号码，1=开出。"""
    df = _chronological(df)
    red_cols = get_red_columns()
    lo, hi = (RED_MIN, RED_MAX) if ball_type == "red" else (BLUE_MIN, BLUE_MAX)
    rows: list[dict] = []

    for _, row in df.iterrows():
        record: dict = {"期号": str(row["期号"])}
        if ball_type == "red":
            drawn = {int(row[c]) for c in red_cols}
        else:
            drawn = {int(row["蓝球"])}
        for n in range(lo, hi + 1):
            record[f"{n:02d}"] = 1 if n in drawn else 0
        rows.append(record)

    return pd.DataFrame(rows).set_index("期号")
