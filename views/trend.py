import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core.history import load_history, slice_history
from core.trend import build_distribution_matrix, build_metric_timeline, build_omission_timeline

st.title("走势图")

history_df = load_history()
if history_df.empty:
    st.warning("请先在「历史开奖」页面拉取数据")
    st.stop()

periods = st.selectbox("显示期数", [30, 50, 80, 100, 150], index=1)
window_df = slice_history(history_df, periods)

tab_omit_red, tab_omit_blue, tab_metric, tab_matrix = st.tabs(
    ["红球遗漏走势", "蓝球遗漏走势", "和值/跨度走势", "号码分布矩阵"]
)

with tab_omit_red:
    omit_red = build_omission_timeline(window_df, "red")
    default_nums = st.multiselect(
        "选择红球号码（可多选）",
        options=list(range(1, 34)),
        default=[1, 6, 12, 18, 24, 33],
        format_func=lambda x: f"{x:02d}",
    )
    if default_nums:
        chart_df = omit_red[omit_red["号码"].isin(default_nums)].copy()
        chart_df["号码"] = chart_df["号码"].apply(lambda x: f"{x:02d}")
        fig = px.line(chart_df, x="期号", y="遗漏", color="号码", markers=True)
        fig.update_layout(height=460, xaxis_title="期号", yaxis_title="遗漏期数", hovermode="x unified")
        fig.update_traces(line=dict(width=2))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("请至少选择一个红球号码")

with tab_omit_blue:
    omit_blue = build_omission_timeline(window_df, "blue")
    blue_nums = st.multiselect(
        "选择蓝球号码",
        options=list(range(1, 17)),
        default=[1, 4, 8, 12, 16],
        format_func=lambda x: f"{x:02d}",
    )
    if blue_nums:
        chart_df = omit_blue[omit_blue["号码"].isin(blue_nums)].copy()
        chart_df["号码"] = chart_df["号码"].apply(lambda x: f"{x:02d}")
        fig = px.line(chart_df, x="期号", y="遗漏", color="号码", markers=True)
        fig.update_layout(height=460, xaxis_title="期号", yaxis_title="遗漏期数")
        st.plotly_chart(fig, use_container_width=True)

with tab_metric:
    metric_df = build_metric_timeline(window_df)
    metric = st.radio("指标", ["和值", "跨度", "奇数个数", "蓝球"], horizontal=True)
    fig = px.line(metric_df, x="期号", y=metric, markers=True)
    fig.update_layout(height=420, xaxis_title="期号", yaxis_title=metric)
    fig.update_traces(line=dict(color="#ff4d4f" if metric != "蓝球" else "#1890ff", width=2))
    st.plotly_chart(fig, use_container_width=True)

with tab_matrix:
    ball_type = st.radio("矩阵类型", ["红球", "蓝球"], horizontal=True)
    matrix_df = build_distribution_matrix(window_df, "red" if ball_type == "红球" else "blue")
    fig = px.imshow(
        matrix_df.values,
        x=matrix_df.columns,
        y=matrix_df.index,
        color_continuous_scale=["#ffffff", "#ff4d4f"] if ball_type == "红球" else ["#ffffff", "#1890ff"],
        aspect="auto",
    )
    fig.update_layout(height=560, xaxis_title="号码", yaxis_title="期号")
    st.plotly_chart(fig, use_container_width=True)
