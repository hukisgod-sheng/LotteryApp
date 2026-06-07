import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from core.ui import render_disclaimer

st.set_page_config(
    page_title="炸裂双色球数据沙盘",
    page_icon="🎱",
    layout="wide",
    initial_sidebar_state="expanded",
)

pg = st.navigation(
    {
        "数据沙盘": [
            st.Page("views/home.py", title="摇号模拟", icon="🎲", default=True),
            st.Page("views/history.py", title="历史开奖", icon="📜"),
            st.Page("views/deduction.py", title="号码推演", icon="🧠"),
            st.Page("views/trend.py", title="走势图", icon="📈"),
            st.Page("views/lucky_guess.py", title="幸运侠几吧猜", icon="🧬"),
        ],
    },
    position="sidebar",
    expanded=True,
)

pg.run()
render_disclaimer()
