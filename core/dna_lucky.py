import hashlib
import math
import re
from dataclasses import dataclass

import numpy as np
import pandas as pd

from core.constants import BLUE_MAX, BLUE_MIN, RED_COUNT, RED_MAX, RED_MIN
from core.cosmic_curves import CosmicPattern, CurveTrace, build_cosmic_pattern, sample_markers
from core.history import frequency_stats
from core.marker_styles import MarkerStyle, pick_marker_styles
from core.models import UserGroup, extract_lucky_nums


def parse_number_group(text: str) -> UserGroup | None:
    text = text.strip()
    if not text or text.startswith("#"):
        return None

    parts = re.split(r"[\s,，+]+", text)
    nums = [int(p) for p in parts if p.strip().isdigit() and 0 <= int(p) <= 999]
    if not nums:
        return None
    return UserGroup(lucky_nums=nums)


def parse_slot_inputs(values: list[int | None]) -> list[UserGroup]:
    """从若干数字框解析用户心仪号码（0-999），填几个都行。"""
    nums = [v for v in values if v is not None and 0 < v <= 999]
    if not nums:
        return []
    return [UserGroup(lucky_nums=nums)]


def parse_user_groups(raw_text: str) -> list[UserGroup]:
    groups: list[UserGroup] = []
    for line in raw_text.splitlines():
        group = parse_number_group(line)
        if group:
            groups.append(group)
    return groups


def _helix_value(t: float, phase: float, scale: float) -> float:
    x = math.sin(t * 1.2 + phase)
    y = math.cos(t * 0.9 + phase * 1.618)
    z = math.sin(t * 2.1 + phase * 0.7) * math.cos(t * 1.5)
    return (x + y + z) / 3.0 * scale


def _build_dna_weights(user_groups: list[UserGroup], history_df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    red_w = np.zeros(RED_MAX + 1)
    blue_w = np.zeros(BLUE_MAX + 1)

    for group in user_groups:
        for n in extract_lucky_nums(group):
            if n <= 0:
                continue
            red_w[(n % RED_MAX) + 1] += 2.0
            blue_w[(n % BLUE_MAX) + 1] += 1.5

    if not history_df.empty:
        red_freq, blue_freq = frequency_stats(history_df)
        max_red = max(red_freq["出现次数"].max(), 1)
        max_blue = max(blue_freq["出现次数"].max(), 1)
        for _, row in red_freq.iterrows():
            red_w[int(row["号码"])] += float(row["出现次数"]) / max_red
        for _, row in blue_freq.iterrows():
            blue_w[int(row["号码"])] += float(row["出现次数"]) / max_blue

    red_w[0] = 0
    blue_w[0] = 0
    if red_w.sum() == 0:
        red_w[RED_MIN:RED_MAX + 1] = 1
    if blue_w.sum() == 0:
        blue_w[BLUE_MIN:BLUE_MAX + 1] = 1
    return red_w, blue_w


def _pick_from_weights(weights: np.ndarray, count: int, lo: int, hi: int, phase: float) -> list[int]:
    pool = list(range(lo, hi + 1))
    chosen: list[int] = []
    for i in range(count):
        adjusted = np.array([weights[n] * (1 + 0.35 * _helix_value(i + 1, phase + n * 0.17, 1.0)) for n in pool])
        adjusted = np.clip(adjusted, 0.001, None)
        for n in chosen:
            idx = pool.index(n)
            adjusted[idx] = 0
        if adjusted.sum() <= 0:
            remaining = [n for n in pool if n not in chosen]
            chosen.append(remaining[i % len(remaining)])
            continue
        probs = adjusted / adjusted.sum()
        pick = int(np.random.choice(pool, p=probs))
        chosen.append(pick)
    return sorted(chosen)


def _dna_seed(user_groups: list[UserGroup], history_df: pd.DataFrame) -> float:
    payload = "|".join(",".join(map(str, extract_lucky_nums(g))) for g in user_groups)
    if not history_df.empty:
        payload += "|" + str(history_df.iloc[0]["期号"])
    digest = hashlib.sha256(payload.encode()).hexdigest()
    return int(digest[:8], 16) / 0xFFFFFFFF


@dataclass
class DnaEvolutionResult:
    tickets: list[tuple[list[int], int]]
    pattern_label: str
    traces: list[CurveTrace]
    marker_points: list[tuple[float, float, float, int]]
    marker_styles: list[MarkerStyle]


def evolve_dna_tickets(
    user_groups: list[UserGroup],
    history_df: pd.DataFrame,
    count: int = 5,
) -> DnaEvolutionResult:
    np.random.seed(int(_dna_seed(user_groups, history_df) * 1_000_000) % (2**32 - 1))
    red_w, blue_w = _build_dna_weights(user_groups, history_df)
    seed = _dna_seed(user_groups, history_df)
    cosmic: CosmicPattern = build_cosmic_pattern(user_groups, seed)

    tickets: list[tuple[list[int], int]] = []
    for gen in range(count):
        phase = seed * (gen + 1) * math.pi
        reds = _pick_from_weights(red_w, RED_COUNT, RED_MIN, RED_MAX, phase)
        blue = _pick_from_weights(blue_w, 1, BLUE_MIN, BLUE_MAX, phase + 1.3)[0]
        tickets.append((reds, blue))

    markers = sample_markers(cosmic.path_x, cosmic.path_y, cosmic.path_z, count)
    lucky_nums: list[int] = []
    for g in user_groups:
        lucky_nums.extend(extract_lucky_nums(g))
    styles = pick_marker_styles(lucky_nums, seed, count)

    return DnaEvolutionResult(
        tickets=tickets,
        pattern_label=cosmic.label,
        traces=cosmic.traces,
        marker_points=markers,
        marker_styles=styles,
    )
