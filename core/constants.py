from pathlib import Path

RED_MIN, RED_MAX = 1, 33
RED_COUNT = 6
BLUE_MIN, BLUE_MAX = 1, 16

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
HISTORY_CSV = DATA_DIR / "ssq_history.csv"

ZHCW_LIST_URL = "https://kaijiang.zhcw.com/zhcw/html/ssq/list_1.html"
ZHCW_PAGE_URL = "https://kaijiang.zhcw.com/zhcw/inc/ssq/ssq_wqhg.jsp?pageNum={page}"
