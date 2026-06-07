import streamlit as st

from core.history import (
    frequency_stats,
    load_history,
    omission_stats,
    recommend_ticket,
    red_blue_lists,
    slice_history,
)
from core.lottery import check_prize
from core.ui import render_inline_numbers, render_ticket

st.title("号码推演")
st.caption("基于历史开奖数据的冷热号、遗漏值与策略推荐")

history_df = load_history()
if history_df.empty:
    st.warning("请先在「历史开奖」页面拉取数据，或运行 `python scripts/fetch_history.py --pages 10 --merge`")
    st.stop()

window = st.selectbox("统计窗口（最近 N 期）", [30, 50, 100, 200, 500, "全部"], index=1)
window_df = slice_history(history_df, None if window == "全部" else int(window))
st.info(f"当前基于最近 **{len(window_df)}** 期开奖数据进行推演")

tab_hot, tab_omit, tab_recommend, tab_verify = st.tabs(
    ["冷热号分析", "遗漏值分析", "策略推演", "号码验奖"]
)

red_freq, blue_freq = frequency_stats(window_df)
red_omit, blue_omit = omission_stats(window_df)

with tab_hot:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**红球出现频次**")
        st.bar_chart(red_freq.set_index("号码")["出现次数"], height=280)
        hot_red = red_freq.nlargest(6, "出现次数")
        cold_red = red_freq.nsmallest(6, "出现次数")
        st.markdown("热号 Top 6")
        for _, row in hot_red.iterrows():
            st.markdown(
                f'<span style="color:#ff4d4f;font-weight:700;">{int(row["号码"]):02d}</span> — {int(row["出现次数"])} 次',
                unsafe_allow_html=True,
            )
        st.markdown("冷号 Top 6")
        for _, row in cold_red.iterrows():
            st.markdown(
                f'<span style="color:#ff4d4f;">{int(row["号码"]):02d}</span> — {int(row["出现次数"])} 次',
                unsafe_allow_html=True,
            )

    with col2:
        st.markdown("**蓝球出现频次**")
        st.bar_chart(blue_freq.set_index("号码")["出现次数"], height=280)
        hot_blue = blue_freq.nlargest(3, "出现次数")
        cold_blue = blue_freq.nsmallest(3, "出现次数")
        st.markdown("热号 Top 3")
        for _, row in hot_blue.iterrows():
            st.markdown(
                f'<span style="color:#1890ff;font-weight:700;">{int(row["号码"]):02d}</span> — {int(row["出现次数"])} 次',
                unsafe_allow_html=True,
            )
        st.markdown("冷号 Top 3")
        for _, row in cold_blue.iterrows():
            st.markdown(
                f'<span style="color:#1890ff;">{int(row["号码"]):02d}</span> — {int(row["出现次数"])} 次',
                unsafe_allow_html=True,
            )

with tab_omit:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**红球遗漏期数**（越大表示越久未出）")
        st.bar_chart(red_omit.set_index("号码")["遗漏期数"], height=280)
    with col2:
        st.markdown("**蓝球遗漏期数**")
        st.bar_chart(blue_omit.set_index("号码")["遗漏期数"], height=280)

with tab_recommend:
    strategy = st.radio(
        "推演策略",
        ["热号优先", "冷号回补", "高遗漏", "均衡随机"],
        horizontal=True,
    )
    if st.button("🔮 生成推演号码", type="primary", use_container_width=True):
        reds, blue, note = recommend_ticket(window_df, strategy)
        st.session_state["recommend_ticket"] = (reds, blue, note, strategy)

    if "recommend_ticket" in st.session_state:
        reds, blue, note, strategy = st.session_state["recommend_ticket"]
        st.success(f"策略：**{strategy}** — {note}")
        render_ticket(reds, blue)
        render_inline_numbers(reds, blue)

with tab_verify:
    st.markdown("输入一注号码，对照指定期开奖结果验奖")
    issue_options = history_df["期号"].astype(str).tolist()
    selected_issue = st.selectbox("选择期号", issue_options)
    row = history_df[history_df["期号"].astype(str) == selected_issue].iloc[0]
    draw_reds, draw_blue = red_blue_lists(row)

    st.markdown("**该期开奖号码**")
    render_inline_numbers(draw_reds, draw_blue)

    c1, c2 = st.columns([3, 1])
    with c1:
        red_input = st.text_input("红球（6 个，空格或逗号分隔）", placeholder="例如：01 05 12 18 25 33")
    with c2:
        blue_input = st.number_input("蓝球", min_value=1, max_value=16, value=1)

    if st.button("✅ 验奖", use_container_width=True):
        try:
            user_reds = sorted({int(x) for x in red_input.replace(",", " ").split() if x.strip()})
            if len(user_reds) != 6:
                st.error("红球必须是 6 个不重复号码（1-33）")
            elif any(n < 1 or n > 33 for n in user_reds):
                st.error("红球范围应为 1-33")
            else:
                level, desc = check_prize(user_reds, int(blue_input), draw_reds, draw_blue)
                red_hits = len(set(user_reds) & set(draw_reds))
                blue_hit = int(blue_input) == draw_blue
                st.markdown("**你的号码**")
                render_inline_numbers(user_reds, int(blue_input))
                if level:
                    st.success(f"命中 {red_hits} 红 + {'1' if blue_hit else '0'} 蓝 → **{desc}**")
                else:
                    st.warning(f"命中 {red_hits} 红 + {'1' if blue_hit else '0'} 蓝 → {desc}")
        except ValueError:
            st.error("号码格式有误，请检查输入")
