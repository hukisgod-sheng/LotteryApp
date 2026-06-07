import importlib
import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import core.cosmic_curves as cosmic_curves
import core.cosmic_names as cosmic_names
import core.dna_lucky as dna_lucky
import core.marker_styles as marker_styles
import core.models as models

importlib.reload(models)
importlib.reload(marker_styles)
importlib.reload(cosmic_names)
importlib.reload(cosmic_curves)
importlib.reload(dna_lucky)

DnaEvolutionResult = dna_lucky.DnaEvolutionResult
evolve_dna_tickets = dna_lucky.evolve_dna_tickets
parse_slot_inputs = dna_lucky.parse_slot_inputs

from core.history import load_history


def _render_cosmic_chart(result: DnaEvolutionResult) -> None:
    fig = go.Figure()
    for trace in result.traces:
        fig.add_trace(
            go.Scatter3d(
                x=trace.x,
                y=trace.y,
                z=trace.z,
                mode="lines",
                line=dict(color=trace.color, width=trace.width, dash=trace.dash or "solid"),
                showlegend=False,
                hoverinfo="skip",
            )
        )

    styles = getattr(result, "marker_styles", None) or []
    for i, point in enumerate(result.marker_points):
        x, y, z, label = point
        style = styles[i] if i < len(styles) else None
        symbol = style.symbol_3d if style else "circle"
        color = style.color if style else "#ff4d4f"
        size = style.size if style else 9
        tag = style.tag if style else "节点"
        fig.add_trace(
            go.Scatter3d(
                x=[x],
                y=[y],
                z=[z],
                mode="markers+text",
                marker=dict(size=size, color=color, symbol=symbol, line=dict(width=1, color="#fff")),
                text=[f"组{label}"],
                textposition="top center",
                showlegend=False,
                hovertemplate=f"第组{label} · {tag}<extra></extra>",
            )
        )

    fig.update_layout(
        height=420,
        margin=dict(l=0, r=0, t=10, b=0),
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            bgcolor="rgba(250,250,250,0.8)",
        ),
    )
    st.plotly_chart(fig, use_container_width=True)
    style_hint = ""
    if styles:
        style_hint = " · " + " / ".join(f"组{i+1}:{s.tag}" for i, s in enumerate(styles))
    st.caption(f"本次星图主题：**{result.pattern_label}**{style_hint}")


def _render_ticket_chart(tickets: list[tuple[list[int], int]], styles: list | None = None) -> None:
    fig = go.Figure()
    group_labels = [f"第{i}组" for i in range(1, 6)]

    for gi, (reds, blue) in enumerate(tickets, start=1):
        style = styles[gi - 1] if styles and gi - 1 < len(styles) else None
        red_color = style.color if style else "#ff4d4f"
        red_symbol = style.symbol if style else "circle"
        fig.add_trace(
            go.Scatter(
                x=[gi] * len(reds),
                y=reds,
                mode="markers+text",
                text=[f"{n:02d}" for n in reds],
                textposition="top center",
                textfont=dict(size=11, color=red_color),
                marker=dict(size=14, color=red_color, symbol=red_symbol),
                showlegend=False,
                hovertemplate=f"第{gi}组 红球 %{{text}}<extra></extra>",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[gi],
                y=[blue],
                mode="markers+text",
                text=[f"{blue:02d}"],
                textposition="bottom center",
                textfont=dict(size=11, color="#1890ff"),
                marker=dict(size=16, color="#1890ff", symbol="diamond"),
                showlegend=False,
                hovertemplate=f"第{gi}组 蓝球 {blue:02d}<extra></extra>",
            )
        )

    fig.update_layout(
        height=200,
        margin=dict(l=40, r=20, t=10, b=40),
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(1, 6)),
            ticktext=group_labels,
            title="",
            range=[0.4, 5.6],
            fixedrange=True,
        ),
        yaxis=dict(title="", range=[0, 35], dtick=5, fixedrange=True),
        plot_bgcolor="#fafafa",
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_ticket_list(tickets: list[tuple[list[int], int]], styles: list | None = None) -> None:
    styles = styles or []
    ball_style = (
        "display:inline-block;min-width:42px;text-align:center;"
        "font-size:26px;font-weight:700;line-height:1.4;"
    )
    for gi, (reds, blue) in enumerate(tickets, start=1):
        style = styles[gi - 1] if gi - 1 < len(styles) else None
        accent = style.color if style else "#ff4d4f"
        tag = f"<span style='color:{accent};font-size:20px;'>({style.tag})</span>" if style else ""
        red_html = "".join(
            f"<span style='{ball_style}color:{accent};'>{n:02d}</span>" for n in reds
        )
        blue_html = f"<span style='{ball_style}color:#1890ff;margin-left:12px;'>+ {blue:02d}</span>"
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:20px;margin:14px 0;padding:14px 18px;
            background:linear-gradient(90deg,#fff5f5,#f0f7ff);border-radius:10px;border:1px solid #f0f0f0;">
                <div style="min-width:130px;font-size:24px;font-weight:700;white-space:nowrap;">
                    第{gi}组 {tag}
                </div>
                <div style="flex:1;display:flex;flex-wrap:wrap;align-items:center;gap:6px 4px;">
                    {red_html}{blue_html}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


st.title("幸运侠几吧猜")
st.caption("填入你喜欢的号码，生成 5 组幸运号码")

history_df = load_history()
if history_df.empty:
    st.warning("请先在「历史开奖」页面拉取数据")

st.markdown("**心仪号码**（每格 0～999，填几个都行，不填也能生成）")

cols = st.columns(10)
slot_values: list[int | None] = []
for i, col in enumerate(cols):
    with col:
        val = col.number_input(
            f"号码{i + 1}",
            min_value=0,
            max_value=999,
            value=0,
            step=1,
            label_visibility="collapsed",
            key=f"lucky_slot_{i}",
        )
        slot_values.append(int(val) if val > 0 else None)

groups = parse_slot_inputs(slot_values)
filled = [v for v in slot_values if v is not None and v > 0]
if filled:
    st.caption(f"已填 {len(filled)} 个号码：" + " ".join(str(n) for n in filled))

if st.button("生成幸运号码", type="primary", use_container_width=True):
    try:
        result = evolve_dna_tickets(groups, history_df, count=5)
        st.session_state["lucky_result"] = result
    except Exception as exc:
        st.session_state.pop("lucky_result", None)
        st.error(f"生成失败：{exc}")
        st.caption("请刷新页面后重试。")

if "lucky_result" in st.session_state:
    result: DnaEvolutionResult = st.session_state["lucky_result"]
    tickets = result.tickets

    _render_cosmic_chart(result)

    st.subheader("幸运号码")
    _render_ticket_chart(tickets, getattr(result, "marker_styles", None))

    _render_ticket_list(tickets, getattr(result, "marker_styles", None))
