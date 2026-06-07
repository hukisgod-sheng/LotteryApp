"""命令行拉取双色球历史开奖数据。

示例:
    python scripts/fetch_history.py --pages 10
    python scripts/fetch_history.py --pages 50 --merge
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.history import fetch_history, load_history, merge_history, save_history


def main() -> None:
    parser = argparse.ArgumentParser(description="拉取中彩网双色球历史开奖数据")
    parser.add_argument("--pages", type=int, default=10, help="抓取页数，每页约 20 期")
    parser.add_argument("--merge", action="store_true", help="与本地 CSV 合并去重")
    args = parser.parse_args()

    print(f"正在拉取最近 {args.pages} 页数据…")
    new_df = fetch_history(pages=args.pages)
    print(f"本次获取 {len(new_df)} 期")

    if args.merge:
        existing = load_history()
        df = merge_history(existing, new_df)
        print(f"合并后共 {len(df)} 期")
    else:
        df = new_df

    path = save_history(df)
    print(f"已保存到 {path}")


if __name__ == "__main__":
    main()
