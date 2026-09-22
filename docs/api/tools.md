# API 参考 · 工具层

ActuarialPilot 提供 7 个 LangChain @tool，LLM Agent 可直接调用。

## pricing_tool

为寿险产品定价。

| 参数 | 说明 |
|---|---|
| `age` | 投保年龄 (18-65) |
| `sex` | "M" / "F" |
| `sum_assured` | 保额（元） |
| `term` | 保险期（终身寿险设为 100） |
| `interest_rate` | 预定利率（小数） |
| `product` | "term" / "whole" / "endowment" |
| `expense_load` | 费用率，默认 0.05 |
| `profit_margin` | 利润率，默认 0.10 |

## sensitivity_tool

对一款定价模型做敏感性分析（利率±50bp、死亡率±10%、保额±10%）。

## reserve_tool

责任准备金评估（prospective / retrospective / zillmer）。

## mortality_tool

查询某年龄的死亡率/生存概率。

## plot_premium_curve_tool

绘制"均衡保费随投保年龄变化"曲线，返回 base64 PNG。

## plot_sensitivity_tornado_tool

绘制敏感性龙卷风图，返回 base64 PNG。

## search_knowledge_base_tool

在条款知识库中检索，返回 JSON 含 answer + sources。

## generate_report_tool

生成 Markdown 报告。

## 使用示例

```python
from actuarial_pilot.tools import pricing_tool

result = pricing_tool.invoke({
    "age": 30, "sex": "M", "sum_assured": 500_000,
    "term": 20, "interest_rate": 0.03,
})
print(result)
```