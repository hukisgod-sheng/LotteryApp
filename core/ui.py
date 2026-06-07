import streamlit as st


def render_ball(number: int, color: str) -> str:
    bg = "#ff4d4f" if color == "red" else "#1890ff"
    return (
        f'<span style="display:inline-block;min-width:52px;height:52px;line-height:52px;'
        f"margin:0 8px 8px 0;border-radius:50%;background:{bg};color:#fff;"
        f'font-size:22px;font-weight:700;text-align:center;">{number:02d}</span>'
    )


def render_ticket(reds: list[int], blue: int) -> None:
    red_html = "".join(render_ball(n, "red") for n in reds)
    blue_html = render_ball(blue, "blue")
    st.markdown(
        f"""
        <div style="padding:24px;border-radius:16px;background:linear-gradient(135deg,#fff5f5,#f0f7ff);
        border:2px solid #ffd6d6;margin:16px 0;">
            <div style="margin-bottom:12px;font-size:18px;font-weight:600;color:#333;">红球</div>
            <div>{red_html}</div>
            <div style="margin:20px 0 12px;font-size:18px;font-weight:600;color:#333;">蓝球</div>
            <div>{blue_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_inline_numbers(reds: list[int], blue: int) -> None:
    red_text = " ".join(
        f'<span style="color:#ff4d4f;font-size:24px;font-weight:700;">{n:02d}</span>' for n in reds
    )
    st.markdown(
        f'<p style="font-size:20px;">{red_text} '
        f'<span style="color:#1890ff;font-size:24px;font-weight:700;">+ {blue:02d}</span></p>',
        unsafe_allow_html=True,
    )


def render_disclaimer() -> None:
    st.markdown(
        """
        <div style="margin-top:48px;padding:16px 12px 8px;border-top:1px solid #e8e8e8;">
            <p style="font-size:11px;line-height:1.65;color:#999;text-align:center;margin:0 0 6px;">
                <strong style="color:#aaa;font-weight:600;">免责声明</strong>：
                本软件仅供娱乐、编程学习与技术研究，不构成任何投注、理财或投资建议。
                历史数据来自互联网公开渠道，不保证完整、准确或及时。
                摇号、推演、模拟结果均为算法生成，与官方福彩中心无关，不能预测真实开奖。
                彩票具有随机性，请理性购彩、量力而行；如需参与，请通过
                <a href="https://www.cwl.gov.cn/" target="_blank" rel="noopener noreferrer"
                   style="color:#bbb;text-decoration:underline;">中国福利彩票官方渠道</a>
                购买，为公益事业尽一份力。
            </p>
            <p style="font-size:10px;color:#bbb;text-align:center;margin:0;">
                炸裂双色球数据沙盘 · 非商业开源学习项目 · 使用者需自行承担使用风险
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
