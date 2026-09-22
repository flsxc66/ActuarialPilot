"""Streamlit 主入口。

启动方式
--------
.. code-block:: bash

    streamlit run actuarial_pilot/ui/streamlit_app.py
"""

from __future__ import annotations

import json

import streamlit as st

from actuarial_pilot import __version__
from actuarial_pilot.agents import Orchestrator
from actuarial_pilot.core.life_table import load_default_table
from actuarial_pilot.core.pricing import level_premium
from actuarial_pilot.core.sensitivity import (
    default_perturbations,
    sensitivity_analysis,
    tornado_plot,
)
from actuarial_pilot.rag.qa import ActuarialQA


# ============== 页面配置 ==============

st.set_page_config(
    page_title="ActuarialPilot",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============== 状态初始化 ==============

@st.cache_resource
def get_orchestrator() -> Orchestrator:
    return Orchestrator()


@st.cache_resource
def get_qa() -> ActuarialQA:
    return ActuarialQA()


# ============== 侧边栏 ==============

with st.sidebar:
    st.title("🧮 ActuarialPilot")
    st.caption(f"v{__version__} · 对话式精算 Agent 工具箱")
    page = st.radio(
        "功能导航",
        ["🎯 智能对话", "💰 定价试算", "📊 敏感性分析", "📚 知识问答", "ℹ️ 关于"],
        label_visibility="collapsed",
    )
    st.divider()

    with st.expander("⚙️ 知识库管理", expanded=False):
        if st.button("🔄 重建索引"):
            with st.spinner("正在入索引..."):
                qa = get_qa()
                count = qa.ingest()
                st.success(f"已写入 {count} 个 chunk")

        if st.button("🗑️ 清空对话历史"):
            st.session_state.pop("messages", None)
            st.success("已清空")


# ============== 页面：智能对话 ==============

if page == "🎯 智能对话":
    st.header("🎯 智能对话")
    st.caption("一句话驱动精算计算。例：'给 30 岁男性、50 万保额、20 年期的定期寿险定个价，利率 3%'")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("请输入你的需求...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("精算 Agent 思考中..."):
                try:
                    orch = get_orchestrator()
                    result = orch.run(user_input)
                    output = result.get("output", "Agent 无输出")
                    st.markdown(output)
                    st.session_state.messages.append({"role": "assistant", "content": output})
                except Exception as e:  # noqa: BLE001
                    err = f"⚠️ 错误：{e}"
                    st.error(err)
                    st.session_state.messages.append({"role": "assistant", "content": err})


# ============== 页面：定价试算 ==============

elif page == "💰 定价试算":
    st.header("💰 寿险产品定价")
    st.caption("无需 LLM，纯精算公式实时计算。")

    c1, c2, c3 = st.columns(3)
    with c1:
        age = st.number_input("投保年龄", 18, 65, 30)
        sex = st.selectbox("性别", ["M", "F"], format_func=lambda x: "男" if x == "M" else "女")
    with c2:
        product = st.selectbox("产品类型", ["term", "whole", "endowment"],
                               format_func=lambda x: {"term": "定期寿险", "whole": "终身寿险", "endowment": "两全险"}[x])
        term = st.number_input("保险期(年)", 5, 100, 20)
    with c3:
        sum_assured = st.number_input("保额（元）", 10_000, 10_000_000, 500_000, step=10_000)
        interest_rate = st.slider("预定利率", 0.01, 0.08, 0.03, 0.005, format="%.3f")

    if st.button("🚀 计算保费", type="primary"):
        try:
            table = load_default_table(sex)
            actual_term = 100 if product == "whole" else term
            from actuarial_pilot.core.pricing import (
                gross_premium,
                net_single_premium,
            )
            nsp = net_single_premium(sum_assured, age, sex, actual_term, interest_rate, table, product)
            net = level_premium(sum_assured, age, sex, actual_term, interest_rate, table, product)
            gross = gross_premium(net)

            c1, c2, c3 = st.columns(3)
            c1.metric("趸交净保费", f"¥{nsp:,.0f}")
            c2.metric("均衡净保费", f"¥{net:,.0f}")
            c3.metric("毛保费（含费用+利润）", f"¥{gross:,.0f}")

            st.success(
                f"**{age}岁{'男' if sex == 'M' else '女'}性，{sum_assured/10000:.0f}万保额，{term}年期**\n\n"
                f"- 生命表：{table.name}\n"
                f"- 利率：{interest_rate*100:.1f}%\n"
                f"- 年缴毛保费：**¥{gross:,.2f}**"
            )
        except Exception as e:  # noqa: BLE001
            st.error(f"计算失败：{e}")


# ============== 页面：敏感性分析 ==============

elif page == "📊 敏感性分析":
    st.header("📊 敏感性分析")
    st.caption("对定价模型的利率 / 死亡率 / 保额做单因素扰动。")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        age = st.number_input("年龄", 18, 65, 30, key="sens_age")
    with c2:
        sex = st.selectbox("性别", ["M", "F"], key="sens_sex",
                           format_func=lambda x: "男" if x == "M" else "女")
    with c3:
        term = st.number_input("期限", 5, 40, 20, key="sens_term")
    with c4:
        interest_rate = st.number_input("基础利率", 0.01, 0.08, 0.03, 0.005,
                                       key="sens_rate", format="%.3f")

    sum_assured = st.number_input("保额", 10_000, 10_000_000, 500_000, key="sens_sum")

    if st.button("📊 跑敏感性", type="primary"):
        table = load_default_table(sex)

        def metric(p):
            return level_premium(
                sum_assured=p["sum_assured"], age=p["age"], sex=p["sex"],
                term=p["term"], interest_rate=p["interest_rate"], table=table,
            )

        result = sensitivity_analysis(
            {"age": age, "sex": sex, "sum_assured": sum_assured, "term": term, "interest_rate": interest_rate},
            metric,
            default_perturbations(),
        )
        st.metric("基准保费", f"¥{result.base_value:,.2f}")
        st.markdown("### 敏感度表格")
        st.dataframe(result.results.style.format({"abs_change": "{:.2f}", "pct_change": "{:.2%}"}))
        st.markdown("### 龙卷风图")
        st.image(tornado_plot(result), use_container_width=True)


# ============== 页面：知识问答 ==============

elif page == "📚 知识问答":
    st.header("📚 保险条款 / 精算研报问答")
    st.caption("基于 RAG 的中文条款问答，每条回答都附原文出处。")

    question = st.text_input("请输入问题", "犹豫期是几天？退保会有损失吗？")

    if st.button("🔍 提问", type="primary"):
        with st.spinner("检索中..."):
            try:
                qa = get_qa()
                result = qa.ask(question, top_k=3)
                st.markdown("### 回答")
                st.markdown(result["answer"])
                if result["sources"]:
                    with st.expander("📎 引用来源"):
                        for i, src in enumerate(result["sources"], 1):
                            st.markdown(f"**[{i}] {src['name']}**（第 {src['page']} 页）")
                            st.caption(src["snippet"])
            except Exception as e:  # noqa: BLE001
                st.error(f"问答失败：{e}。请先在侧边栏点击'重建索引'。")


# ============== 页面：关于 ==============

elif page == "ℹ️ 关于":
    st.header("ℹ️ 关于 ActuarialPilot")
    st.markdown(
        f"""
ActuarialPilot v{__version__} 是面向寿险精算师的开源 AI Agent 工具箱。

**核心特性**
- 🧮 **精算引擎**：定期/终身/两全保险定价、敏感性、责任准备金
- 🤖 **AI Agent**：LangChain + LangGraph + DeepSeek-V3（可换 OpenAI/Qwen）
- 📚 **RAG 问答**：Chroma 向量库 + 中文友好 Embedding
- 🎮 **Web UI**：Streamlit 一键启动

**技术栈**
- Python 3.10+ / LangChain 0.2 / LangGraph / Chroma / Streamlit
- 数据：中国人身保险业经验生命表（CLA2020，合成参考数据）

**GitHub**：https://github.com/flsxc66/ActuarialPilot
"""
    )


def main() -> None:
    """Streamlit 主入口函数。"""
    pass  # 全部逻辑已通过页面级条件分支完成


if __name__ == "__main__":
    main()