import random

from core.constants import BLUE_MAX, BLUE_MIN, RED_COUNT, RED_MAX, RED_MIN


def draw_one_ticket() -> tuple[list[int], int]:
    reds = sorted(random.sample(range(RED_MIN, RED_MAX + 1), RED_COUNT))
    blue = random.randint(BLUE_MIN, BLUE_MAX)
    return reds, blue


def check_prize(user_reds: list[int], user_blue: int, draw_reds: list[int], draw_blue: int) -> tuple[int, str]:
    red_hits = len(set(user_reds) & set(draw_reds))
    blue_hit = user_blue == draw_blue

    if red_hits == 6 and blue_hit:
        return 1, "一等奖 (6+1)"
    if red_hits == 6:
        return 2, "二等奖 (6+0)"
    if red_hits == 5 and blue_hit:
        return 3, "三等奖 (5+1)"
    if red_hits == 5 or (red_hits == 4 and blue_hit):
        return 4, "四等奖 (5+0 或 4+1)"
    if red_hits == 4 or (red_hits == 3 and blue_hit):
        return 5, "五等奖 (4+0 或 3+1)"
    if blue_hit and red_hits <= 2:
        return 6, "六等奖 (2+1 / 1+1 / 0+1)"
    return 0, "未中奖"
