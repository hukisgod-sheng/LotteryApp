import random
import re
import time
from collections import Counter
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

from core.constants import (
    BLUE_MAX,
    BLUE_MIN,
    DATA_DIR,
    HISTORY_CSV,
    RED_MAX,
    RED_MIN,
    ZHCW_LIST_URL,
    ZHCW_PAGE_URL,
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

COLUMNS = ["期号", "开奖日期", "红1", "红2", "红3", "红4", "红5", "红6", "蓝球", "销售额"]


def _new_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(HEADERS)
    session.get(ZHCW_LIST_URL, timeout=15)
    return session


def _parse_page(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("tr")[2:-1]
    records: list[dict] = []

    for row in rows:
        tds = row.find_all("td")
        if len(tds) < 3:
            continue
        ems = tds[2].find_all("em")
        if len(ems) < 7:
            continue
        nums = [int(e.get_text(strip=True)) for e in ems]
        reds = sorted(nums[:6])
        blue = nums[6]
        sale_text = tds[3].get_text(strip=True) if len(tds) > 3 else ""
        sale = int(re.sub(r"[^\d]", "", sale_text) or 0)
        records.append(
            {
                "期号": tds[1].get_text(strip=True),
                "开奖日期": tds[0].get_text(strip=True),
                "红1": reds[0],
                "红2": reds[1],
                "红3": reds[2],
                "红4": reds[3],
                "红5": reds[4],
                "红6": reds[5],
                "蓝球": blue,
                "销售额": sale,
            }
        )
    return records


def _get_total_pages(session: requests.Session) -> int:
    resp = session.get(ZHCW_LIST_URL, timeout=15)
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")
    strong = soup.find_all("p")[1].find("strong")
    return int(strong.get_text(strip=True)) if strong else 1


def fetch_page(page: int = 1, session: requests.Session | None = None) -> list[dict]:
    owns_session = session is None
    session = session or _new_session()
    try:
        resp = session.get(ZHCW_PAGE_URL.format(page=page), timeout=15)
        resp.encoding = "utf-8"
        if resp.status_code != 200:
            return []
        return _parse_page(resp.text)
    finally:
        if owns_session:
            session.close()


def fetch_history(pages: int = 5, delay: float = 0.3) -> pd.DataFrame:
    session = _new_session()
    total_pages = min(pages, _get_total_pages(session))
    all_records: list[dict] = []

    for page in range(1, total_pages + 1):
        records = fetch_page(page, session=session)
        if not records:
            session.close()
            session = _new_session()
            time.sleep(delay)
            records = fetch_page(page, session=session)
        all_records.extend(records)
        if page < total_pages:
            time.sleep(delay)

    session.close()

    df = pd.DataFrame(all_records, columns=COLUMNS)
    if df.empty:
        return df
    return df.drop_duplicates(subset=["期号"]).sort_values("期号", ascending=False).reset_index(drop=True)


def save_history(df: pd.DataFrame, path: Path = HISTORY_CSV) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return path


def load_history(path: Path = HISTORY_CSV) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=COLUMNS)
    df = pd.read_csv(path, dtype={"期号": str})
    return df.sort_values("期号", ascending=False).reset_index(drop=True)


def merge_history(existing: pd.DataFrame, new_data: pd.DataFrame) -> pd.DataFrame:
    if existing.empty:
        return new_data
    if new_data.empty:
        return existing
    merged = pd.concat([existing, new_data], ignore_index=True)
    return merged.drop_duplicates(subset=["期号"]).sort_values("期号", ascending=False).reset_index(drop=True)


def get_red_columns() -> list[str]:
    return ["红1", "红2", "红3", "红4", "红5", "红6"]


def slice_history(df: pd.DataFrame, last_n: int | None) -> pd.DataFrame:
    if df.empty:
        return df
    if last_n is None or last_n <= 0 or last_n >= len(df):
        return df.copy()
    return df.head(last_n).copy()


def red_blue_lists(row: pd.Series) -> tuple[list[int], int]:
    reds = [int(row[c]) for c in get_red_columns()]
    return reds, int(row["蓝球"])


def frequency_stats(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    red_cols = get_red_columns()
    red_counter: Counter[int] = Counter()
    blue_counter: Counter[int] = Counter()

    for _, row in df.iterrows():
        for col in red_cols:
            red_counter[int(row[col])] += 1
        blue_counter[int(row["蓝球"])] += 1

    red_df = pd.DataFrame(
        {
            "号码": list(range(RED_MIN, RED_MAX + 1)),
            "出现次数": [red_counter.get(n, 0) for n in range(RED_MIN, RED_MAX + 1)],
            "类型": "红球",
        }
    )
    blue_df = pd.DataFrame(
        {
            "号码": list(range(BLUE_MIN, BLUE_MAX + 1)),
            "出现次数": [blue_counter.get(n, 0) for n in range(BLUE_MIN, BLUE_MAX + 1)],
            "类型": "蓝球",
        }
    )
    return red_df, blue_df


def omission_stats(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    red_omit = {n: len(df) for n in range(RED_MIN, RED_MAX + 1)}
    blue_omit = {n: len(df) for n in range(BLUE_MIN, BLUE_MAX + 1)}
    red_cols = get_red_columns()

    for idx, (_, row) in enumerate(df.iterrows()):
        reds = {int(row[c]) for c in red_cols}
        blue = int(row["蓝球"])
        for n in range(RED_MIN, RED_MAX + 1):
            if n in reds and red_omit[n] == len(df):
                red_omit[n] = idx
        for n in range(BLUE_MIN, BLUE_MAX + 1):
            if n == blue and blue_omit[n] == len(df):
                blue_omit[n] = idx

    red_df = pd.DataFrame({"号码": list(red_omit.keys()), "遗漏期数": list(red_omit.values()), "类型": "红球"})
    blue_df = pd.DataFrame({"号码": list(blue_omit.keys()), "遗漏期数": list(blue_omit.values()), "类型": "蓝球"})
    return red_df, blue_df


def recommend_ticket(df: pd.DataFrame, strategy: str) -> tuple[list[int], int, str]:
    red_df, blue_df = frequency_stats(df)
    red_omit, blue_omit = omission_stats(df)

    if strategy == "热号优先":
        reds = sorted(red_df.nlargest(6, "出现次数")["号码"].astype(int).tolist())
        blue = int(blue_df.nlargest(1, "出现次数")["号码"].iloc[0])
        note = "选取统计窗口内出现次数最多的 6 个红球 + 1 个蓝球"
    elif strategy == "冷号回补":
        reds = sorted(red_df.nsmallest(6, "出现次数")["号码"].astype(int).tolist())
        blue = int(blue_df.nsmallest(1, "出现次数")["号码"].iloc[0])
        note = "选取统计窗口内出现次数最少的 6 个红球 + 1 个蓝球"
    elif strategy == "高遗漏":
        reds = sorted(red_omit.nlargest(6, "遗漏期数")["号码"].astype(int).tolist())
        blue = int(blue_omit.nlargest(1, "遗漏期数")["号码"].iloc[0])
        note = "选取当前遗漏期数最大的 6 个红球 + 1 个蓝球"
    else:
        hot_reds = set(red_df.nlargest(10, "出现次数")["号码"].astype(int))
        cold_reds = set(red_df.nsmallest(10, "出现次数")["号码"].astype(int))
        pool = sorted(hot_reds | cold_reds)
        reds = sorted(random.sample(pool, 6))
        blue = int(blue_df.sample(1)["号码"].iloc[0])
        note = "从热号 Top10 与冷号 Top10 的并集中随机抽取 6 个红球，蓝球随机"

    return reds, blue, note
