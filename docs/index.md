# ActuarialPilot

> 让精算师用一句话完成定价、敏感性分析与条款问答的开源 AI Agent 工具箱

## 三句话价值主张

1. **精算公式 + AI Agent**：把寿险定价、敏感性、责任准备金封装成 LLM 可调用的工具
2. **教材级严谨**：29 条单元测试覆盖所有核心公式，可解释、可审计
3. **3 周可上线**：Streamlit 一键启动，云端部署零成本

## 主要模块

- 🧮 [精算核心](api/core.md) — 寿险定价、准备金、敏感性、年金
- 🤖 [智能体层](api/agents.md) — LangChain + LangGraph 多 Agent 路由
- 🛠️ [工具层](api/tools.md) — 7 个 LLM 可调用函数
- 📚 [RAG 子系统](api/rag.md) — 中文友好条款问答

## 立即开始

```bash
git clone https://github.com/flsxc66/ActuarialPilot
cd ActuarialPilot
pip install -r requirements.txt
python scripts/generate_life_table.py
streamlit run actuarial_pilot/ui/streamlit_app.py
```

## 路线图

- ✅ M0 · 核心引擎 + Agent + RAG + Web Demo
- ⏳ M1 · 年金 / 健康险 + 报告导出
- ⏳ M2 · 多 LLM 适配 + Docker
- ⏳ M3 · 接入 Prophet / Axis