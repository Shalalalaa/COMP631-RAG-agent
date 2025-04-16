# backend/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from retriever.retriever import (
    DenseRetrievalExactSearch,
    hybrid_emotion_search,
    corpus_sci,
    corpus_folk,
    corpus_freud,
    model,
    emotion_model
)
import json
import torch

# 创建 FastAPI 实例
app = FastAPI()

# 配置跨域中间件，允许所有源访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议修改为具体的前端地址
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定义请求体模型
class QueryRequest(BaseModel):
    text: str

# 定义响应体模型
class ResponseModel(BaseModel):
    answer: str
    sources: list[str]
    emotions: list[str]
    sci_texts: list[str]
    folk_texts: list[str]
    freud_texts: list[str]

@app.post("/analyze", response_model=ResponseModel)
async def analyze_dream(request: QueryRequest):
    """
    接收前端发送的梦境描述，调用混合检索和情绪分析，
    生成梦境分析报告（目前模拟返回响应）。
    """
    try:
        # 调用混合语义+情绪检索：对科学文献进行检索和情绪标签提取
        sci_results, emotions = hybrid_emotion_search(request.text, top_k=3)
        
        # 使用普通的向量检索对周公解梦和弗洛伊德进行搜索
        folk_results = retriever_folk.search(corpus_folk, {"query": request.text}, top_k=3)
        freud_results = retriever_freud.search(corpus_freud, {"query": request.text}, top_k=3)

        # 提取检索结果中的标题信息
        sci_titles = [corpus_sci[doc_id]["text"] for doc_id in sci_results.keys()]
        folk_titles = [corpus_folk[doc_id]["text"] for doc_id in folk_results.get("query", {}).keys()]
        freud_titles = [corpus_freud[doc_id]["text"] for doc_id in freud_results.get("query", {}).keys()]

        # 构造给 LLM 的提示（后续可以替换为实际的LLM调用）
        prompt = f"""
        基于以下研究数据，请用中文生成通俗易懂的梦境分析报告：
        
        【科学文献】:
        {json.dumps(sci_titles[:2], ensure_ascii=False)}
        
        【民俗解释】: 
        {json.dumps(folk_titles[:2], ensure_ascii=False)}
        
        【精神分析】:
        {json.dumps(freud_titles[:2], ensure_ascii=False)}
        
        用户梦境描述：
        {request.text}
        """
        print("生成的LLM提示：", prompt)  # 可打印提示用于调试

        # 模拟 LLM 调用（后续可替换为实际调用接口）
        answer = "[模拟响应] 根据最新研究，您的梦境可能与焦虑情绪相关..."

        return {
            "answer": answer,
            "sources": sci_titles[:3],
            "emotions": emotions,
            "sci_titles": sci_titles[:3],
            "folk_titles": folk_titles[:3],
            "freud_titles": freud_titles[:3]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # 使用 uvicorn 直接启动 FastAPI 服务
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
