# 架构

ActuarialPilot 采用**5 层分层架构**，从下到上：

```
┌──────────────────────────────────────────────────────────────────┐
│  Layer 4 · 表现层 Presentation                                    │
│  Streamlit Web UI  /  CLI  /  Jupyter Notebook                   │
├──────────────────────────────────────────────────────────────────┤
│  Layer 3 · 智能体层 Agent                                         │
│  PricingAgent · UnderwritingAgent · Orchestrator                 │
│  编排：LangChain LCEL / LangGraph 状态机                          │
├──────────────────────────────────────────────────────────────────┤
│  Layer 2 · 工具层 Tools (LLM 可调用)                              │
│  pricing / sensitivity / reserve / mortality / plot / search / report│
├──────────────────────────────────────────────────────────────────┤
│  Layer 1 · 精算核心引擎 Core (纯 Python, 无 LLM 依赖)             │
│  life_table · pricing · reserve · sensitivity · annuity          │
├──────────────────────────────────────────────────────────────────┤
│  Layer 0 · 数据层 Data                                           │
│  CLA2020 生命表 + 产品条款 PDF + Chroma VectorStore              │
└──────────────────────────────────────────────────────────────────┘
```

## 设计原则

### 1. 公式与 LLM 解耦

Layer 1 完全无 LLM 依赖，可以脱离 AI 单独使用：

```python
from actuarial_pilot.core.pricing import level_premium
from actuarial_pilot.core.life_table import load_default_table

table = load_default_table("M")
premium = level_premium(500_000, 30, "M", 20, 0.03, table)
```

这意味着：
- **可审计**：精算公式都看得见，可被监管验收
- **可测试**：教材例题级回归测试
- **可复用**：脱离 LLM 也能用

### 3. LLM 只做"理解 + 调度 + 表达"

LLM 三个职责：

| 职责 | 工具 |
|---|---|
| 理解用户意图 | LangChain Agent |
| 调度合适的工具 | @tool 装饰器 |
| 把 JSON 结果包装成中文 | LCEL Chain |

**绝不**让 LLM 直接做数值计算。

### 3. 数据约定

- 年龄：整数
- 利率：小数（0.03 = 3%）
- 保额/保费：人民币元
- 生命表：qx 是 0-1 概率，lx 是从 100,000 起的生存人数

## 数据流

以"定期寿险定价"对话为例：

```
用户: "给 30 岁男性、50 万保额、20 年期的定期寿险定个价，利率 3%"
        │
        ▼
[Streamlit / CLI] → 传给 PricingAgent
        │
        ▼
[LangChain Agent] LLM 解析意图 → 调用 pricing_tool(...)
        │
        ▼
[Tools 层] pricing_tool 是壳，内部调用 core.pricing.level_premium(...)
        │
        ▼
[Core 引擎] 用 CLA2020 生命表 + 利率 3% 精算现值
        │
        ▼
返回 JSON: {annual_premium: 1234.56, net_single_premium: ..., assumptions: {...}}
        │
        ▼
[Agent] LLM 把 JSON 包装成中文自然语言回答
        │
        ▼
[Streamlit] 渲染回答 + 提供"下载报告"按钮
```