from dataclasses import dataclass

DRAWS_PER_YEAR = 156


@dataclass(frozen=True)
class StrategyProfile:
    key: str
    name: str
    tip: str
    hot: float
    cold: float
    omit: float
    recent: float
    chaos: float
    repeat_last: float


STRATEGY_PROFILES: tuple[StrategyProfile, ...] = (
    StrategyProfile("aggressive", "激进型", "追热号、跟趋势，波动大", 2.8, 0.2, 0.4, 2.0, 0.6, 0.15),
    StrategyProfile("moderate", "缓和型", "冷热均衡，走势平滑", 1.2, 1.2, 1.0, 1.0, 0.3, 0.25),
    StrategyProfile("conservative", "保守型", "偏冷号与遗漏回补", 0.3, 2.5, 2.2, 0.4, 0.15, 0.1),
    StrategyProfile("lowkey", "闷骚型", "表面随机、暗偏遗漏", 0.8, 1.5, 1.8, 0.6, 0.9, 0.2),
    StrategyProfile("stubborn", "固执型", "延续上期相似号码", 1.0, 0.5, 0.8, 2.5, 0.2, 2.8),
    StrategyProfile("reverse", "逆转型", "与近期走势反向选择", 0.4, 2.0, 1.5, 0.2, 0.5, 0.05),
    StrategyProfile("momentum", "顺势型", "强化近期连出号码", 2.2, 0.4, 0.6, 2.4, 0.35, 0.4),
    StrategyProfile("contrarian", "逆势型", "刻意避开热门号码", 0.2, 2.8, 1.2, 0.1, 0.45, 0.05),
    StrategyProfile("stable", "稳健型", "中间频段优先", 1.0, 1.0, 1.2, 0.8, 0.15, 0.3),
    StrategyProfile("radical", "激进派", "高热号集中出击", 3.2, 0.1, 0.3, 1.6, 0.7, 0.1),
    StrategyProfile("gentle", "温和型", "低波动、偏均值", 1.1, 1.1, 0.9, 0.9, 0.2, 0.35),
    StrategyProfile("cautious", "谨慎型", "遗漏优先、热号次之", 0.6, 1.8, 2.5, 0.5, 0.15, 0.15),
    StrategyProfile("bold", "大胆型", "高随机+高热号", 2.0, 0.6, 0.5, 1.2, 1.2, 0.2),
    StrategyProfile("timid", "胆小型", "偏冷偏稳、少冒险", 0.5, 2.2, 1.6, 0.4, 0.1, 0.2),
    StrategyProfile("flexible", "灵活型", "随窗口动态切换权重", 1.4, 1.4, 1.1, 1.1, 0.5, 0.3),
    StrategyProfile("rigid", "僵化型", "固定偏好上期号码", 0.7, 0.7, 0.9, 1.5, 0.1, 2.2),
    StrategyProfile("dreamer", "幻想型", "高随机探索组合", 1.0, 1.0, 1.0, 0.8, 1.5, 0.25),
    StrategyProfile("realist", "现实型", "紧贴历史统计", 1.8, 1.2, 1.3, 1.0, 0.2, 0.2),
    StrategyProfile("gambler", "搏冷型", "专挑冷门号码", 0.2, 3.0, 1.0, 0.2, 0.8, 0.05),
    StrategyProfile("follower", "跟热型", "热号权重拉满", 3.0, 0.2, 0.5, 1.8, 0.4, 0.25),
    StrategyProfile("lonewolf", "独狼型", "低重复、偏散列", 1.2, 1.6, 1.4, 0.3, 0.6, 0.05),
    StrategyProfile("team", "抱团型", "偏连号与邻近号", 1.6, 0.8, 0.9, 1.4, 0.3, 0.35),
    StrategyProfile("scatter", "散点型", "号码分布尽量分散", 1.0, 1.3, 1.2, 0.6, 0.4, 0.1),
    StrategyProfile("focus", "聚焦型", "集中在小范围热区", 2.4, 0.5, 0.7, 1.5, 0.25, 0.3),
    StrategyProfile("vortex", "漩涡型", "围绕上期号码波动", 1.3, 1.0, 1.1, 2.0, 0.55, 1.6),
    StrategyProfile("linear", "线性型", "和值趋势推演", 1.2, 1.2, 1.0, 1.2, 0.25, 0.2),
    StrategyProfile("wave", "波动型", "冷热交替曲线", 1.5, 1.5, 1.3, 0.9, 0.45, 0.15),
    StrategyProfile("pulse", "脉冲型", "周期性强化热号", 2.1, 0.9, 0.8, 1.3, 0.5, 0.2),
    StrategyProfile("silent", "静默型", "接近均匀、微调", 0.9, 0.9, 1.0, 0.7, 0.15, 0.15),
    StrategyProfile("explosive", "爆发型", "极端热号+高波动", 3.0, 0.3, 0.4, 1.7, 0.9, 0.1),
    StrategyProfile("zen", "佛系型", "低干预、轻权重", 0.8, 0.8, 0.9, 0.6, 0.2, 0.2),
    StrategyProfile("sly", "狡黠型", "热冷混搭迷惑式", 1.6, 1.7, 1.0, 0.9, 0.65, 0.15),
    StrategyProfile("honest", "耿直型", "纯历史频率排序", 2.0, 0.5, 1.0, 0.8, 0.1, 0.2),
    StrategyProfile("romantic", "浪漫型", "偏小号区间", 1.3, 1.1, 1.0, 0.9, 0.5, 0.2),
    StrategyProfile("logic", "逻辑型", "偏大号区间", 1.3, 1.1, 1.0, 0.9, 0.5, 0.2),
    StrategyProfile("chaos", "混沌型", "强随机扰动", 1.0, 1.0, 1.0, 0.5, 1.8, 0.1),
    StrategyProfile("order", "秩序型", "低随机、重规律", 1.5, 1.3, 1.4, 1.0, 0.05, 0.25),
    StrategyProfile("pioneer", "先锋型", "试探未出号码", 0.6, 2.0, 2.0, 0.4, 0.55, 0.08),
    StrategyProfile("guard", "守成型", "延续稳定热号", 2.2, 0.6, 1.2, 1.0, 0.2, 0.35),
    StrategyProfile("flash", "闪电型", "快速跟进最新一期", 1.8, 0.7, 0.6, 2.6, 0.5, 0.5),
    StrategyProfile("iron", "钢铁型", "固定偏好、低变化", 1.4, 0.9, 1.5, 0.7, 0.08, 0.6),
    StrategyProfile("mist", "迷雾型", "高噪声平滑曲线", 1.0, 1.0, 1.2, 0.8, 1.0, 0.15),
    StrategyProfile("sun", "太阳型", "偏奇数组合", 1.2, 1.0, 1.0, 1.0, 0.35, 0.2),
    StrategyProfile("moon", "月亮型", "偏偶数组合", 1.2, 1.0, 1.0, 1.0, 0.35, 0.2),
    StrategyProfile("tiger", "猛虎型", "大幅偏离均值", 1.7, 1.6, 1.3, 1.1, 0.75, 0.12),
    StrategyProfile("crane", "闲鹤型", "温和偏移、小步调", 1.0, 1.2, 1.1, 0.8, 0.25, 0.22),
    StrategyProfile("dragon", "潜龙型", "长期遗漏突然回补", 0.5, 1.5, 2.8, 0.5, 0.4, 0.1),
    StrategyProfile("phoenix", "凤凰型", "热号延续后再切换", 2.3, 0.8, 0.9, 1.6, 0.45, 0.3),
    StrategyProfile("star", "星轨型", "综合曲线加权", 1.3, 1.3, 1.2, 1.1, 0.4, 0.25),
    StrategyProfile("comet", "彗星型", "尾部冷号、头部热号", 2.0, 1.8, 1.0, 0.7, 0.55, 0.1),
    StrategyProfile("mirror", "镜像型", "对上期号码对称变换", 1.0, 1.0, 1.0, 1.8, 0.35, 1.2),
    StrategyProfile("shadow", "影子型", "轻微跟随上期", 1.2, 0.9, 1.0, 1.9, 0.3, 1.0),
    StrategyProfile("spark", "火花型", "小样本高波动", 1.6, 1.4, 0.8, 1.4, 0.85, 0.18),
    StrategyProfile("anchor", "锚定型", "围绕历史均值", 1.1, 1.1, 1.3, 0.9, 0.12, 0.28),
    StrategyProfile("free", "自由型", "权重均衡随机", 1.0, 1.0, 1.0, 1.0, 0.6, 0.2),
)


def get_strategy(name: str) -> StrategyProfile:
    for s in STRATEGY_PROFILES:
        if s.name == name:
            return s
    return STRATEGY_PROFILES[0]


def strategy_names() -> list[str]:
    return [s.name for s in STRATEGY_PROFILES]


def resolve_window_periods(periods: int, years: float) -> int:
    from_years = int(years * DRAWS_PER_YEAR) if years and years > 0 else 0
    return max(int(periods), from_years, 1)
