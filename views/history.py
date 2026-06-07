import streamlit as st

from core.history import fetch_history, load_history, merge_history, save_history

st.title("历史开奖数据")
st.caption("从中彩网拉取双色球历史开奖号码，保存到本地 CSV")

history_df = load_history()
local_count = len(history_df)

col_a, col_b, col_c = st.columns(3)
col_a.metric("本地已有期数", local_count)
if not history_df.empty:
    col_b.metric("最新期号", history_df.iloc[0]["期号"])
    col_c.metric("最早期号", history_df.iloc[-1]["期号"])

st.divider()

fetch_pages = st.slider("拉取页数（每页约 20 期）", min_value=1, max_value=50, value=5)
merge_mode = st.checkbox("与本地数据合并（推荐）", value=True)

if st.button("⬇️ 拉取历史开奖号码", type="primary", use_container_width=True):
    try:
        with st.spinner(f"正在从中彩网拉取 {fetch_pages} 页数据…"):
            new_df = fetch_history(pages=fetch_pages)
            df = merge_history(history_df, new_df) if merge_mode else new_df
            save_history(df)
        st.success(f"拉取完成！本次获取 {len(new_df)} 期，本地共 {len(df)} 期")
        st.rerun()
    except Exception as exc:
        st.error(f"拉取失败：{exc}")
        st.info("也可在终端运行：`python scripts/fetch_history.py --pages 10 --merge`")

st.divider()

history_df = load_history()
if history_df.empty:
    st.warning("暂无本地历史数据，请点击上方按钮拉取，或运行 `python scripts/fetch_history.py --pages 10 --merge`")
else:
    show_n = st.selectbox("显示最近", [20, 50, 100, 200, "全部"], index=0)
    display_df = history_df if show_n == "全部" else history_df.head(int(show_n))
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    csv_bytes = history_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        "下载完整 CSV",
        data=csv_bytes,
        file_name="ssq_history.csv",
        mime="text/csv",
    )
