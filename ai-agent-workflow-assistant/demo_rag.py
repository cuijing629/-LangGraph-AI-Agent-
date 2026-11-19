from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="演示知识库")


class Query(BaseModel):
    query: str
    document_id: str | None = None
    top_k: int = Field(default=5, ge=1, le=20)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/retrieve")
def retrieve(payload: Query):
    topics = [
        "使用 @app.get 和 @app.post 定义路由，练习路径和查询参数。",
        "使用 Pydantic BaseModel 定义请求体，练习字段验证。",
        "使用 FastAPI TestClient 测试成功与失败的接口调用。",
    ]
    matches = (
        "fastapi" in payload.query.lower()
        and payload.document_id in (None, "fastapi-demo")
    )
    chunks = [
        {
            "filename": "FastAPI-演示资料.md",
            "document_id": "fastapi-demo",
            "page": index,
            "text": topic,
            "score": round(1 - index * 0.03, 2),
        }
        for index, topic in enumerate(topics[:payload.top_k], 1)
    ]
    return {"score_kind": "similarity", "chunks": chunks if matches else []}
