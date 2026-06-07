import hashlib
from dataclasses import dataclass

# Plotly Scatter3d 仅支持以下 symbol
SCATTER3D_SYMBOLS = frozenset(
    {"circle", "circle-open", "cross", "diamond", "diamond-open", "square", "square-open", "x"}
)

SYMBOL_3D_FALLBACK = {
    "triangle-up": "diamond",
    "triangle-down": "diamond",
    "pentagon": "square",
    "hexagon": "square",
    "hexagon2": "square",
    "octagon": "square",
    "star": "diamond",
    "hexagram": "diamond",
    "star-triangle-up": "diamond",
    "star-square": "square",
    "star-diamond": "diamond",
    "diamond-tall": "diamond",
    "hourglass": "diamond",
    "bowtie": "cross",
    "circle-cross": "cross",
    "circle-x": "x",
    "square-cross": "cross",
    "square-x": "x",
    "diamond-cross": "cross",
    "diamond-x": "x",
}


def to_scatter3d_symbol(symbol: str) -> str:
    if symbol in SCATTER3D_SYMBOLS:
        return symbol
    return SYMBOL_3D_FALLBACK.get(symbol, "circle")


@dataclass(frozen=True)
class MarkerStyle:
    symbol: str
    color: str
    size: int
    tag: str

    @property
    def symbol_3d(self) -> str:
        return to_scatter3d_symbol(self.symbol)


_BASE_SHAPES = ("circle", "circle-open", "diamond", "diamond-open", "square", "square-open", "cross", "x")

_PALETTE = (
    "#ff4d4f", "#1890ff", "#52c41a", "#faad14", "#722ed1", "#eb2f96", "#13c2c2", "#fa541c",
    "#2f54eb", "#a0d911", "#f759ab", "#ffc53d", "#597ef7", "#ff85c0", "#5cdbd3", "#ffd666",
    "#95de64", "#ff7875", "#69c0ff", "#b37feb", "#ff9c6e", "#36cfc9", "#bae637", "#ffd43b",
    "#51cf66", "#ff922b", "#cc5de8", "#20c997", "#fcc419", "#845ef7", "#339af0", "#e64980",
    "#12b886", "#fab005", "#228be6", "#be4bdb", "#40c057", "#fd7e14", "#15aabf", "#868e96",
)

_TAGS = (
    "恒星", "钻石", "方块", "十字", "叉号", "圆环", "菱环", "方环",
    "金星", "火星", "木星", "水星", "土星", "天王星", "海王星", "冥王星",
    "流星", "彗星", "脉冲", "超新星", "白矮", "红巨", "中子", "黑洞",
    "星云", "星团", "光年", "轨道", "日冕", "耀斑", "极光", "引力",
    "量子", "光子", "中微", "暗物质", "反物质", "奇点", "膨胀", "坍缩",
)


def _build_marker_pool() -> tuple[MarkerStyle, ...]:
    pool: list[MarkerStyle] = []
    for i, color in enumerate(_PALETTE):
        shape = _BASE_SHAPES[i % len(_BASE_SHAPES)]
        tag = _TAGS[i % len(_TAGS)]
        size = 9 + (i % 4)
        pool.append(MarkerStyle(shape, color, size, tag))
    extras = [
        MarkerStyle("circle", "#ff4d4f", 12, "炸裂星"),
        MarkerStyle("diamond", "#1890ff", 12, "电光钻"),
        MarkerStyle("cross", "#faad14", 12, "雷逼十字"),
        MarkerStyle("square", "#52c41a", 11, "幸运方"),
        MarkerStyle("x", "#722ed1", 11, "玄学叉"),
        MarkerStyle("circle-open", "#eb2f96", 11, "欧皇环"),
        MarkerStyle("diamond-open", "#13c2c2", 11, "非酋菱"),
    ]
    pool.extend(extras)
    return tuple(pool)


MARKER_POOL: tuple[MarkerStyle, ...] = _build_marker_pool()


def pick_marker_styles(user_nums: list[int], seed: float, count: int = 5) -> list[MarkerStyle]:
    payload = f"marker|{','.join(map(str, sorted(user_nums)))}|{seed:.8f}|{count}"
    digest = hashlib.sha256(payload.encode()).hexdigest()
    picked: list[MarkerStyle] = []
    used: set[int] = set()
    offset = 0
    while len(picked) < count and offset < len(digest) - 1:
        idx = (int(digest[offset : offset + 2], 16) + len(picked) * 7) % len(MARKER_POOL)
        if idx not in used:
            used.add(idx)
            picked.append(MARKER_POOL[idx])
        offset += 2
    while len(picked) < count:
        picked.append(MARKER_POOL[len(picked) % len(MARKER_POOL)])
    return picked
