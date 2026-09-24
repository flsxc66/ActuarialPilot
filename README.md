<div align="center">

# 🧮 ActuarialPilot

**让精算师用一句话完成定价、敏感性分析与条款问答的开源 AI Agent 工具箱**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CI](https://github.com/flsxc66/ActuarialPilot/actions/workflows/ci.yml/badge.svg)](https://github.com/flsxc66/ActuarialPilot/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-online-brightgreen.svg)](https://flsxc66.github.io/ActuarialPilot/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

[📖 文档站](https://flsxc66.github.io/ActuarialPilot/) · [🚀 本地运行](#-30-秒启动) · [🐛 报告 Bug](https://github.com/flsxc66/ActuarialPilot/issues)

</div>

---

## ✨ 它能做什么

> **"给 30 岁男性、50 万保额、20 年期的定期寿险定个价，利率 3%"**
>
> → 5 秒后你拿到：均衡保费、趸险生命表来源、敏感性龙卷风图。

| 🧮 精算引擎 | 🤖 AI Agent | 📚 知识问答 |
|---|---|---|
| 定期/终身寿险定价 | 自然语言对话 | 产品条款 RAG |
| 责任准备金评估 | 工具调度与组合 | 精算研报问答 |
| 敏感性分析 | 中文报告生成 | 引用溯源 |
| 年金现值 | 多轮对话记忆 | 监管文件检索 |

## 🎯 适用人群

- 📊 **精算实习生/新人** — 公式不会写？Excel 模板太复杂？来试试一句话定价
- 💼 **保险产品经理** — 想快速试算不同假设？不再依赖精算师
- 🔍 **核保/理赔人员** — 翻条款慢？RAG 问答秒级响应
- 🎓 **学术研究者** — 想批量跑模型？提供 Python API

## 🚀 30 秒启动

```bash
git clone https://github.com/flsxc66/ActuarialPilot
cd ActuarialPilot
pip install -r requirements.txt
cp .env.example .env  # 填入 DEEPSEEK_API_KEY（或其他 OpenAI 兼容服务）

# 生成生命表
python scripts/generate_life_table.py

# 启动 Web UI
streamlit run actuarial_pilot/ui/streamlit_app.py
```

## 🏗 架构

```
┌──────────────────────────────────────────────────────────────────┐
│  Layer 4 · 表现层 (Streamlit / CLI / Jupyter)                     │
├──────────────────────────────────────────────────────────────────┤
│  Layer 3 · 智能体层 (LangChain + LangGraph)                       │
│    PricingAgent · UnderwritingAgent · Orchestrator               │
├──────────────────────────────────────────────────────────────────┤
│  Layer 2 · 工具层 (7 个 @tool)                                    │
├──────────────────────────────────────────────────────────────────┤
│  Layer 1 · 精算核心引擎 (纯 Python, 无 LLM 依赖, 100% 单测覆盖) │
│    life_table · pricing · reserve · sensitivity · annuity        │
├──────────────────────────────────────────────────────────────────┤
│  Layer 0 · 数据层 (CLA2020 生命表 + 条款 PDF + Chroma)          │
```

**关键设计**：LLM 只负责"意图理解 + 工具调度 + 自然语言包装"，所有数值计算走精装公式库，**可解释、可审计、可被监管验收**。

## 📦 模块导航

```
actuarial_pilot/
├── core/       # 精算公式库（纯 Python，可单独使用）
├── tools/      # LangChain @tool 工具
├── agents/     # LangChain Agent + LangGraph 路由
├── rag/        # Chroma + 中文 RAG
├── ui/         # Streamlit Web 界面
└── utils/      # 日志 / IO
```

## 🧪 学术严谨性

所有精算公式均配套 **单元测试 + 教材例题回归**，覆盖：

- 《寿险精算数学》李秀芳 第 3、5 章
- 《Life Contingencies》Bowers 第 5、7 章
- 中国人身保险业经验生命表（CLA2020，参考合成数据）

```bash
pytest tests/ -v
# → 29 passed in 1.05s
```

## 🎯 Roadmap

- ✅ **M0** · 核心引擎 + Agent + RAG + Web Demo
- ⏳ **M1** · 年金 / 健康险 + 报告导出 + 多 LLM 适配
- ⏳ **M2** · Docker + 评估脚本 + 中英双语
- ⏳ **M3** · 接入 Prophet / Axis 真实精算系统
- ⏳ **M4** · SaaS 版本

## 🤝 贡献

欢迎精算同学、AI 工程师、保险产品经理提 Issue / PR！

## 📜 License

MIT © 2026 ActuarialPilot Contributors