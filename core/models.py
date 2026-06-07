from dataclasses import dataclass


@dataclass
class UserGroup:
    lucky_nums: list[int]


def extract_lucky_nums(group: UserGroup | object) -> list[int]:
    """兼容新旧 UserGroup，避免 Streamlit 热重载缓存导致属性不一致。"""
    if hasattr(group, "lucky_nums"):
        return list(group.lucky_nums)
    nums = list(getattr(group, "reds", []))
    blue = getattr(group, "blue", None)
    if blue is not None:
        nums.append(blue)
    return nums
