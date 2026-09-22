# 快速开始

## 1. 安装

### 方式 A：pip

```bash
pip install -r requirements.txt
```

### 方式 B：poetry

```bash
poetry install
```

### 方式 C：开发模式

```bash
pip install -e ".[dev]"
```

## 2. 配置环境变量

复制 `.env.example` 为 `.env`，填入你的 API Key：

```bash
cp .env.example .env
```

推荐使用 DeepSeek（中文友好、便宜）：

```dotenv
OPENAI_API_KEY=sk-your-deepseek-key
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat
```

也支持任何 OpenAI 兼容服务（OpenAI / Qwen / Moonshot / Ollama 等）。

## 3. 生成生命表

```bash
python scripts/generate_life_table.py
```

## 4. 启动 Web UI

```bash
streamlit run actuarial_pilot/ui/streamlit_app.py
```

访问 http://localhost:8501

## 5. 命令行调用

```python
from actuarial_pilot.core.life_table import load_default_table
from actuarial_pilot.core.pricing import level_premium

table = load_default_table("M")
premium = level_premium(
    sum_assured=500_000, age=30, sex="M", term=20,
    interest_rate=0.03, table=table,
)
print(f"年缴毛保费：¥{premium:,.2f}")
```

## 6. 运行测试

```bash
pytest tests/ -v
```

## 下一步

- 📖 [查看架构](architecture.md)
- 🧮 [深入精算核心 API](api/core.md)
- 🤖 [配置 Agent](api/agents.md)