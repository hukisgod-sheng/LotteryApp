import hashlib

import numpy as np
import pandas as pd

from core.constants import BLUE_MAX, BLUE_MIN, RED_COUNT, RED_MAX, RED_MIN
from core.history import frequency_stats, get_red_columns, omission_stats, red_blue_lists, slice_history
from core.strategy_profiles import StrategyProfile


def _build_scores(
    profile: StrategyProfile,
    history_df: pd.DataFrame,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    red_freq, blue_freq = frequency_stats(history_df)
    red_omit, blue_omit = omission_stats(history_df)

    last_reds, last_blue = red_blue_lists(history_df.iloc[0])

    max_red = max(red_freq["出现次数"].max(), 1)
    max_blue = max(blue_freq["出现次数"].max(), 1)
    max_red_omit = max(red_omit["遗漏期数"].max(), 1)
    max_blue_omit = max(blue_omit["遗漏期数"].max(), 1)

    rng = np.random.default_rng(seed)
    red_scores = np.zeros(RED_MAX + 1)
    blue_scores = np.zeros(BLUE_MAX + 1)

    for n in range(RED_MIN, RED_MAX + 1):
        freq = red_freq.loc[red_freq["号码"] == n, "出现次数"].iloc[0]
        omit = red_omit.loc[red_omit["号码"] == n, "遗漏期数"].iloc[0]
        cold = max_red - freq
        recent = 1.0 if n in last_reds else 0.0
        repeat = 1.0 if n in last_reds else 0.0
        chaos = rng.random()
        red_scores[n] = (
            profile.hot * (freq / max_red)
            + profile.cold * (cold / max_red)
            + profile.omit * (omit / max_red_omit)
            + profile.recent * recent
            + profile.repeat_last * repeat
            + profile.chaos * chaos
        )

    for n in range(BLUE_MIN, BLUE_MAX + 1):
        freq = blue_freq.loc[blue_freq["号码"] == n, "出现次数"].iloc[0]
        omit = blue_omit.loc[blue_omit["号码"] == n, "遗漏期数"].iloc[0]
        cold = max_blue - freq
        recent = 1.0 if n == last_blue else 0.0
        repeat = 1.0 if n == last_blue else 0.0
        chaos = rng.random()
        blue_scores[n] = (
            profile.hot * (freq / max_blue)
            + profile.cold * (cold / max_blue)
            + profile.omit * (omit / max_blue_omit)
            + profile.recent * recent
            + profile.repeat_last * repeat
            + profile.chaos * chaos
        )

    red_scores[0] = 0
    blue_scores[0] = 0
    return red_scores, blue_scores


def _pick_weighted(scores: np.ndarray, count: int, lo: int, hi: int, rng: np.random.Generator) -> list[int]:
    pool = list(range(lo, hi + 1))
    chosen: list[int] = []
    for _ in range(count):
        weights = np.array([scores[n] if n not in chosen else 0.0 for n in pool])
        weights = np.clip(weights, 0.001, None)
        if weights.sum() <= 0:
            remain = [n for n in pool if n not in chosen]
            chosen.append(rng.choice(remain))
            continue
        pick = int(rng.choice(pool, p=weights / weights.sum()))
        chosen.append(pick)
    return sorted(chosen)


def predict_next_draw(
    history_df: pd.DataFrame,
    profile: StrategyProfile,
    window_periods: int,
) -> tuple[list[int], int, str, pd.Series | None]:
    if history_df.empty:
        return [], 0, "暂无历史数据，请先在「历史开奖」拉取数据", None

    window_df = slice_history(history_df, window_periods)
    latest = window_df.iloc[0]
    latest_reds, latest_blue = red_blue_lists(latest)

    seed_src = f"{profile.key}|{latest['期号']}|{window_periods}"
    seed = int(hashlib.sha256(seed_src.encode()).hexdigest()[:8], 16)
    rng = np.random.default_rng(seed)

    red_scores, blue_scores = _build_scores(profile, window_df, seed)
    reds = _pick_weighted(red_scores, RED_COUNT, RED_MIN, RED_MAX, rng)
    blue = _pick_weighted(blue_scores, 1, BLUE_MIN, BLUE_MAX, rng)[0]

    note = (
        f"基于最近 **{len(window_df)}** 期数据，参考最新期 **{latest['期号']}** "
        f"（{' '.join(f'{n:02d}' for n in latest_reds)} + {latest_blue:02d}），"
        f"按 **{profile.name}** 曲线推演下一期。"
    )
    return reds, blue, note, latest


def run_strategy_batch_simulation(
    history_df: pd.DataFrame,
    profile: StrategyProfile,
    window_periods: int,
    times: int,
) -> pd.DataFrame:
    window_df = slice_history(history_df, window_periods)
    seed = int(hashlib.sha256(f"batch|{profile.key}|{times}".encode()).hexdigest()[:8], 16)
    red_scores, blue_scores = _build_scores(profile, window_df, seed)
    rng = np.random.default_rng(seed)

    red_counts = {n: 0 for n in range(RED_MIN, RED_MAX + 1)}
    blue_counts = {n: 0 for n in range(BLUE_MIN, BLUE_MAX + 1)}

    for _ in range(times):
        reds = _pick_weighted(red_scores, RED_COUNT, RED_MIN, RED_MAX, rng)
        blue = _pick_weighted(blue_scores, 1, BLUE_MIN, BLUE_MAX, rng)[0]
        for n in reds:
            red_counts[n] += 1
        blue_counts[blue] += 1

    red_df = pd.DataFrame(
        {"号码": list(red_counts.keys()), "出现次数": list(red_counts.values()), "类型": "红球"}
    )
    blue_df = pd.DataFrame(
        {"号码": list(blue_counts.keys()), "出现次数": list(blue_counts.values()), "类型": "蓝球"}
    )
    return pd.concat([red_df, blue_df], ignore_index=True)
