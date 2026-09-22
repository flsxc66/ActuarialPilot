"""验证 .env 中的 LLM 配置是否能正常工作。

运行方式（在项目根目录下）：
    python scripts/test_llm.py

这个脚本只读取本地 .env，不会打印你的 API key。
"""

from __future__ import annotations

import sys
from pathlib import Path

# 保证直接运行本脚本时也能找到项目根目录下的 actuarial_pilot 包
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from actuarial_pilot.agents.llm import get_llm
from actuarial_pilot.config import LLM_CONFIG


def main() -> None:
    print("=" * 50)
    print("ActuarialPilot · LLM 连接测试")
    print("=" * 50)
    print(f"接口地址 : {LLM_CONFIG.base_url}")
    print(f"模型名称 : {LLM_CONFIG.model}")
    key = LLM_CONFIG.api_key
    # 只显示 key 的前 6 位和后 4 位，避免完整泄露到屏幕/截图
    masked = f"{key[:6]}****{key[-4:]}" if len(key) > 12 else "（未配置）"
    print(f"API Key  : {masked}")
    print("-" * 50)

    if not key or key.startswith("sk-your"):
        print("✗ 尚未配置 API Key，请先在项目根目录创建 .env 文件")
        sys.exit(1)

    print("正在连接并请求模型回复，请稍候...")
    try:
        resp = get_llm().invoke("请只回复四个字：连接成功")
    except Exception as e:  # noqa: BLE001
        print(f"✗ 连接失败：{e}")
        print("\n排查建议：")
        print("  1. 检查 .env 里的 key 是否复制完整（无多余空格/换行）")
        print("  2. 检查 OPENAI_BASE_URL 是否正确")
        print("  3. 检查模型名称是否为该平台支持的型号")
        sys.exit(1)

    print(f"模型回复 : {resp.content}")
    print("=" * 50)
    print("✓ 配置有效！可以启动 Streamlit 使用智能对话了")
    print("  py -m streamlit run actuarial_pilot/ui/streamlit_app.py")


if __name__ == "__main__":
    main()