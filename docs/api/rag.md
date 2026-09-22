# API 参考 · RAG 子系统

## ActuarialVectorStore

Chroma 向量库的封装。

```python
from actuarial_pilot.rag.vectorstore import ActuarialVectorStore
vs = ActuarialVectorStore()
vs.add_documents([doc1, doc2])  # 添加 chunk
docs = vs.similarity_search("定期寿险 现金价值", k=3)
```

## ActuarialQA

检索问答链，结合 LLM。

```python
from actuarial_pilot.rag.qa import ActuarialQA

qa = ActuarialQA()
qa.ingest(["data/policies/sample_term_life.md"])  # 入索引
result = qa.ask("犹豫期是几天？")
print(result["answer"])
print(result["sources"])  # 引用来源
```

## Embedding 配置

通过环境变量切换：

- `EMBEDDING_PROVIDER=openai` — OpenAI 兼容（默认）
- `EMBEDDING_PROVIDER=dashscope` — 通义千问
- `EMBEDDING_PROVIDER=local` — 本地 Sentence-Transformers（无需 API key）

## 数据流

```
PDF/MD/TXT → loaders → splitter (中文友好) → embed → Chroma
                                                      ↓
user query ─────────────────────────────────────────→ retrieval
                                                      ↓
                                          Top-K chunks + LLM → answer + sources
```