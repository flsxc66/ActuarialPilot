# API 参考 · Agent 层

## PricingAgent

对话式定价智能体，调用精算工具完成产品定价、敏感性、准备金。

```python
from actuarial_pilot.agents import PricingAgent

agent = PricingAgent()
output = agent.run("给 30 岁男性、50 万保额、20 年期的定期寿险定个价，利率 3%")
print(output)
```

## UnderwritingAgent

基于 RAG 的核保问答智能体。

```python
from actuarial_pilot.agents import UnderwritingAgent
agent = UnderwritingAgent()
output = agent.run("犹豫期是几天？")
```

## Orchestrator

多 Agent 路由器（基于 LangGraph）。根据用户意图自动选 Agent。

```python
from actuarial_pilot.agents import Orchestrator
orch = Orchestrator()
result = orch.run("给我定个价")  # 自动路由到 PricingAgent
```

## ConversationMemory

SQLite 持久化对话记忆。

```python
from actuarial_pilot.agents import ConversationMemory
mem = ConversationMemory(session_id="my_session")
mem.add("user", "你好")
mem.add("assistant", "你好，我是 ActuarialPilot")
history = mem.get_history(limit=10)
```