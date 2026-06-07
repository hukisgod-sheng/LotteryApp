import hashlib
import math
from dataclasses import dataclass
from core.cosmic_names import pick_fantasy_name
from core.models import extract_lucky_nums

import numpy as np


@dataclass
class CurveTrace:
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray
    color: str = "#52c41a"
    width: float = 5
    dash: str | None = None


@dataclass
class CosmicPattern:
    label: str
    traces: list[CurveTrace]
    path_x: np.ndarray
    path_y: np.ndarray
    path_z: np.ndarray


def _rotate_xyz(x, y, z, ax, ay, az):
    cx, sx = math.cos(ax), math.sin(ax)
    cy, sy = math.cos(ay), math.sin(ay)
    cz, sz = math.cos(az), math.sin(az)
    y1 = y * cx - z * sx
    z1 = y * sx + z * cx
    x2 = x * cy + z1 * sy
    z2 = -x * sy + z1 * cy
    x3 = x2 * cz - y1 * sz
    y3 = x2 * sz + y1 * cz
    return x3, y3, z2


def _apply_transform(x, y, z, seed: float):
    ax = seed * math.pi * 2
    ay = seed * math.pi * 1.618
    az = seed * math.pi * 0.707
    scale = 0.85 + (seed * 0.3)
    x, y, z = _rotate_xyz(x, y, z, ax, ay, az)
    return x * scale, y * scale, z * scale


def _interp_path(points: list[tuple[float, float, float]], steps: int = 80) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if len(points) < 2:
        p = points[0] if points else (0.0, 0.0, 0.0)
        return np.array([p[0]]), np.array([p[1]]), np.array([p[2]])

    xs, ys, zs = [], [], []
    seg_steps = max(steps // (len(points) - 1), 8)
    for i in range(len(points) - 1):
        x0, y0, z0 = points[i]
        x1, y1, z1 = points[i + 1]
        for t in np.linspace(0, 1, seg_steps, endpoint=False):
            xs.append(x0 + (x1 - x0) * t)
            ys.append(y0 + (y1 - y0) * t)
            zs.append(z0 + (z1 - z0) * t)
    xs.append(points[-1][0])
    ys.append(points[-1][1])
    zs.append(points[-1][2])
    return np.array(xs), np.array(ys), np.array(zs)


def sample_markers(x, y, z, count: int = 5) -> list[tuple[float, float, float, int]]:
    pts = np.column_stack([x, y, z])
    if len(pts) < 2:
        return [(float(x[0]), float(y[0]), float(z[0]), i + 1) for i in range(count)]

    seg_len = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    dists = np.concatenate([[0.0], np.cumsum(seg_len)])
    total = dists[-1] or 1.0
    markers: list[tuple[float, float, float, int]] = []
    for i in range(count):
        target = total * (i + 1) / (count + 1)
        idx = int(np.searchsorted(dists, target))
        idx = min(max(idx, 0), len(x) - 1)
        markers.append((float(x[idx]), float(y[idx]), float(z[idx]), i + 1))
    return markers


def _pick_pattern_index(user_groups: list, seed: float) -> int:
    nums: list[int] = []
    for g in user_groups:
        nums.extend(extract_lucky_nums(g))
    payload = ",".join(map(str, sorted(nums))) or "0"
    payload += f"|{seed:.6f}"
    digest = hashlib.sha256(payload.encode()).hexdigest()
    return int(digest[:4], 16) % len(PATTERN_BUILDERS)


def _build_helix(seed: float) -> CosmicPattern:
    t = np.linspace(0, 4 * math.pi, 200)
    x = np.sin(t)
    y = np.cos(t)
    z = np.sin(t * 2) * 0.5
    x, y, z = _apply_transform(x, y, z, seed)
    x2, y2, z2 = _apply_transform(-x * 0.8, y * 0.8, z + 0.3, seed * 0.9)
    return CosmicPattern(
        "",
        [
            CurveTrace(x, y, z, "#52c41a", 6),
            CurveTrace(x2, y2, z2, "#1890ff", 4, "dash"),
        ],
        x,
        y,
        z,
    )


def _build_big_dipper(seed: float) -> CosmicPattern:
    stars = [
        (-1.8, 0.6, 0.1),
        (-1.2, 0.5, -0.1),
        (-0.5, 0.0, 0.2),
        (0.0, -0.1, 0.0),
        (0.7, 0.2, -0.15),
        (1.2, 0.5, 0.1),
        (1.9, 0.9, 0.25),
    ]
    x, y, z = _interp_path(stars, 120)
    x, y, z = _apply_transform(x, y, z, seed)
    return CosmicPattern("", [CurveTrace(x, y, z, "#ffd666", 6)], x, y, z)


def _build_solar_system(seed: float) -> CosmicPattern:
    traces: list[CurveTrace] = []
    radii = [0.35, 0.55, 0.75, 0.95, 1.15, 1.35]
    colors = ["#ffa940", "#69c0ff", "#95de64", "#ff7875", "#b37feb", "#ffc069"]
    for r, color in zip(radii, colors):
        t = np.linspace(0, 2 * math.pi, 120)
        x = r * np.cos(t)
        y = r * np.sin(t) * 0.55
        z = np.sin(t * 3 + r) * 0.15
        x, y, z = _apply_transform(x, y, z, seed + r * 0.1)
        traces.append(CurveTrace(x, y, z, color, 3))
    t = np.linspace(0, 2 * math.pi, 80)
    sun_x = 0.08 * np.cos(t)
    sun_y = 0.08 * np.sin(t)
    sun_z = np.zeros_like(t)
    sx, sy, sz = _apply_transform(sun_x, sun_y, sun_z, seed)
    traces.insert(0, CurveTrace(sx, sy, sz, "#ffec3d", 8))
    main = traces[2]
    return CosmicPattern("", traces, main.x, main.y, main.z)


def _build_galaxy(seed: float) -> CosmicPattern:
    t = np.linspace(0, 6 * math.pi, 300)
    r = 0.15 + t * 0.18
    x = r * np.cos(t)
    y = r * np.sin(t)
    z = np.sin(t * 0.8) * 0.25
    x, y, z = _apply_transform(x, y, z, seed)
    x2, y2, z2 = _apply_transform(-x * 0.7, y * 0.7, -z, seed * 1.1)
    return CosmicPattern(
        "",
        [
            CurveTrace(x, y, z, "#b37feb", 5),
            CurveTrace(x2, y2, z2, "#69c0ff", 4, "dash"),
        ],
        x,
        y,
        z,
    )


def _build_orion(seed: float) -> CosmicPattern:
    stars = [
        (-0.3, 1.4, 0.1),
        (0.3, 1.2, -0.05),
        (0.0, 0.6, 0.0),
        (-0.8, 0.0, 0.15),
        (0.8, 0.0, -0.1),
        (-0.5, -0.8, 0.05),
        (0.5, -0.9, 0.0),
        (0.0, -1.5, -0.1),
    ]
    x, y, z = _interp_path(stars, 100)
    x, y, z = _apply_transform(x, y, z, seed)
    return CosmicPattern("", [CurveTrace(x, y, z, "#ff7875", 5)], x, y, z)


def _build_scorpius(seed: float) -> CosmicPattern:
    stars = [
        (-1.6, 0.8, 0.0),
        (-1.0, 0.5, 0.1),
        (-0.4, 0.2, -0.05),
        (0.1, -0.1, 0.0),
        (0.5, -0.5, 0.1),
        (0.9, -0.9, 0.05),
        (1.3, -1.4, -0.1),
        (1.7, -1.0, 0.2),
    ]
    x, y, z = _interp_path(stars, 110)
    x, y, z = _apply_transform(x, y, z, seed)
    return CosmicPattern("", [CurveTrace(x, y, z, "#ff4d4f", 5)], x, y, z)


def _build_cygnus(seed: float) -> CosmicPattern:
    stars = [(0, 1.5, 0), (0, 0.5, 0), (0, -0.5, 0), (-1.2, 0.5, 0.1), (1.2, 0.5, -0.1)]
    x, y, z = _interp_path(stars, 90)
    x, y, z = _apply_transform(x, y, z, seed)
    return CosmicPattern("", [CurveTrace(x, y, z, "#69c0ff", 5)], x, y, z)


def _build_leo(seed: float) -> CosmicPattern:
    stars = [
        (-1.5, 0.3, 0),
        (-0.8, 0.8, 0.1),
        (-0.2, 0.5, -0.05),
        (0.4, 0.2, 0.05),
        (1.0, -0.2, 0),
        (1.5, -0.8, 0.1),
        (0.6, -1.2, -0.05),
    ]
    x, y, z = _interp_path(stars, 100)
    x, y, z = _apply_transform(x, y, z, seed)
    return CosmicPattern("", [CurveTrace(x, y, z, "#ffc53d", 5)], x, y, z)


def _build_andromeda(seed: float) -> CosmicPattern:
    t = np.linspace(0, 4 * math.pi, 200)
    x = 1.2 * np.cos(t)
    y = 0.6 * np.sin(t)
    z = 0.3 * np.sin(t * 2)
    x, y, z = _apply_transform(x, y, z, seed)
    inner_t = np.linspace(0, 2 * math.pi, 80)
    ix = 0.5 * np.cos(inner_t)
    iy = 0.25 * np.sin(inner_t)
    iz = np.zeros_like(inner_t)
    ix, iy, iz = _apply_transform(ix, iy, iz, seed * 1.2)
    return CosmicPattern(
        "",
        [
            CurveTrace(x, y, z, "#ff85c0", 5),
            CurveTrace(ix, iy, iz, "#d3adf7", 3, "dash"),
        ],
        x,
        y,
        z,
    )


def _build_cassiopeia(seed: float) -> CosmicPattern:
    stars = [(-1.2, 0.3, 0), (-0.6, -0.4, 0.1), (0, 0.5, -0.05), (0.6, -0.3, 0.05), (1.2, 0.4, 0)]
    x, y, z = _interp_path(stars, 80)
    x, y, z = _apply_transform(x, y, z, seed)
    return CosmicPattern("", [CurveTrace(x, y, z, "#5cdbd3", 5)], x, y, z)


def _build_ursa_minor(seed: float) -> CosmicPattern:
    stars = [
        (0.0, 1.6, 0.1),
        (0.3, 1.0, -0.05),
        (0.5, 0.4, 0.05),
        (0.2, -0.2, 0),
        (-0.3, -0.6, 0.1),
        (-0.7, -1.0, -0.05),
        (-0.2, -1.5, 0.05),
    ]
    x, y, z = _interp_path(stars, 100)
    x, y, z = _apply_transform(x, y, z, seed)
    return CosmicPattern("", [CurveTrace(x, y, z, "#91d5ff", 5)], x, y, z)


PATTERN_BUILDERS = [
    _build_helix,
    _build_big_dipper,
    _build_solar_system,
    _build_galaxy,
    _build_orion,
    _build_scorpius,
    _build_cygnus,
    _build_leo,
    _build_andromeda,
    _build_cassiopeia,
    _build_ursa_minor,
]


def build_cosmic_pattern(user_groups: list, seed: float) -> CosmicPattern:
    nums: list[int] = []
    for g in user_groups:
        nums.extend(extract_lucky_nums(g))

    geom_idx = _pick_pattern_index(user_groups, seed)
    pattern = PATTERN_BUILDERS[geom_idx](seed)
    label = pick_fantasy_name(nums, seed, geom_idx)
    return CosmicPattern(label, pattern.traces, pattern.path_x, pattern.path_y, pattern.path_z)
