import pandas as pd
import streamlit as st

from core.history import load_history, red_blue_lists
from core.lottery import draw_one_ticket
from core.predict import predict_next_draw, run_strategy_batch_simulation
from core.strategy_profiles import get_strategy, resolve_window_periods, strategy_names
from core.ui import render_inline_numbers, render_ticket

RED_MIN, RED_MAX = 1, 33
BLUE_MIN, BLUE_MAX = 1, 16


st.title("炸裂双色球数据沙盘")
st.caption("随机摇号 · 曲线推演 · 号码热度一览")

history_df = load_history()

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("单注摇号")
    if st.button("🎲 摇一注幸运号码", type="primary", use_container_width=True):
        reds, blue = draw_one_ticket()
        st.session_state["last_ticket"] = (reds, blue)

    if "last_ticket" in st.session_state:
        reds, blue = st.session_state["last_ticket"]
        st.markdown("**本注号码**")
        render_ticket(reds, blue)
        render_inline_numbers(reds, blue)

with col_right:
    st.subheader("曲线推演")

    if history_df.empty:
        st.warning("请先在「历史开奖」拉取数据，才能基于走势推演下一期")
    else:
        latest = history_df.iloc[0]
        lr, lb = red_blue_lists(latest)
        st.caption(f"最新开奖 **{latest['期号']}**：{' '.join(f'{n:02d}' for n in lr)} + {lb:02d}")

    c1, c2 = st.columns(2)
    with c1:
        sim_periods = st.number_input(
            "模拟期数",
            min_value=10,
            max_value=2000,
            value=100,
            step=10,
            key="home_sim_periods",
            help="取最近 N 期历史数据分析",
        )
    with c2:
        sim_years = st.number_input(
            "模拟年数",
            min_value=0.0,
            max_value=20.0,
            value=1.0,
            step=0.5,
            key="home_sim_years",
            help="按年折算期数（约 156 期/年），与期数取较大值",
        )

    window = resolve_window_periods(int(sim_periods), float(sim_years))
    st.caption(f"实际分析窗口：**{window}** 期")

    strategy_name = st.selectbox(
        "推演曲线类型",
        strategy_names(),
        index=0,
        key="home_strategy",
        help="不同曲线类型会使用不同的内部权重公式推演下一期",
    )
    profile = get_strategy(strategy_name)
    st.info(f"**{profile.name}**：{profile.tip}")

    if st.button("📊 推演下一期号码", type="secondary", use_container_width=True):
        if history_df.empty:
            st.error("缺少历史开奖数据")
        else:
            with st.spinner("正在按曲线推演…"):
                reds, blue, note, _ = predict_next_draw(history_df, profile, window)
                if reds:
                    st.session_state["predict_ticket"] = (reds, blue, note, strategy_name, window)
                    stats_df = run_strategy_batch_simulation(history_df, profile, window, min(window, 500))
                    st.session_state["stats_df"] = stats_df
                    st.session_state["sim_meta"] = (strategy_name, window)

    if "predict_ticket" in st.session_state:
        reds, blue, note, used_strategy, used_window = st.session_state["predict_ticket"]
        st.success(note)
        st.markdown("**推演下一期**")
        render_ticket(reds, blue)
        render_inline_numbers(reds, blue)
        st.caption(f"曲线：{used_strategy} · 窗口 {used_window} 期")

    if "stats_df" in st.session_state:
        stats_df = st.session_state["stats_df"]
        meta = st.session_state.get("sim_meta", ("", 0))
        st.success(f"已完成 {meta[1]} 期窗口下的曲线模拟（{meta[0]}）")

        tab_red, tab_blue = st.tabs(["红球热度", "蓝球热度"])

        with tab_red:
            red_df = stats_df[stats_df["类型"] == "红球"].sort_values("号码")
            st.bar_chart(red_df.set_index("号码")["出现次数"], height=320)
            top_red = red_df.nlargest(5, "出现次数")
            st.markdown("**红球 Top 5**")
            for _, row in top_red.iterrows():
                st.markdown(
                    f'<span style="color:#ff4d4f;font-weight:700;">{int(row["号码"]):02d}</span> '
                    f'— 出现 **{int(row["出现次数"])}** 次',
                    unsafe_allow_html=True,
                )

        with tab_blue:
            blue_df = stats_df[stats_df["类型"] == "蓝球"].sort_values("号码")
            st.bar_chart(blue_df.set_index("号码")["出现次数"], height=320)
            top_blue = blue_df.nlargest(3, "出现次数")
            st.markdown("**蓝球 Top 3**")
            for _, row in top_blue.iterrows():
                st.markdown(
                    f'<span style="color:#1890ff;font-weight:700;">{int(row["号码"]):02d}</span> '
                    f'— 出现 **{int(row["出现次数"])}** 次',
                    unsafe_allow_html=True,
                )
