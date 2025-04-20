# # ✅ backend/main.py (升级版)

# import sys
# import os
# import json
# import torch
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from transformers import AutoTokenizer, AutoModelForCausalLM
# from huggingface_hub import hf_hub_download
# from sentence_transformers import SentenceTransformer, util

# # Disable Hugging Face symlink warning
# os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
# os.environ["TRANSFORMERS_NO_TF"] = "1"

# sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
# from retriever.retriever import MemmapRetriever

# # Load summarizer model
# compressor_model = SentenceTransformer("all-MiniLM-L6-v2")

# # Auto device
# device = "cuda" if torch.cuda.is_available() else "cpu"
# print(f"\n🔥 Using device: {device}")

# # Load DeepSeek model
# print("🔄 Loading DeepSeek model...")
# tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B")
# model = AutoModelForCausalLM.from_pretrained(
#     "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
#     torch_dtype=torch.float16 if device == "cuda" else torch.float32,
#     trust_remote_code=True
# ).to(device)
# print("✅ DeepSeek model loaded.\n")

# # Load Retriever
# print("🔄 Loading Retriever...")
# retriever = MemmapRetriever(
#     memmap_path="retriever/corpus_emb.dat",
#     doc_ids_path="retriever/corpus_doc_ids.json",
#     dimension=384,
#     num_docs=len(json.load(open("retriever/corpus_doc_ids.json"))),
#     model_name="Lajavaness/bilingual-embedding-small"
# )
# print("✅ Retriever loaded.\n")

# # Load Corpus
# print("🔄 Downloading corpus.jsonl from Hugging Face...")
# corpus_path = hf_hub_download(
#     repo_id="COMP631GroupSYCZ/Corpus",
#     filename="corpus.jsonl",
#     repo_type="dataset",
#     cache_dir="retriever/hf_cache"
# )

# print("🔄 Loading corpus...")
# corpus = {}
# with open(corpus_path, "r", encoding="utf-8") as f:
#     for line in f:
#         doc = json.loads(line.strip())
#         doc_id = doc["_id"]
#         corpus[doc_id] = {"title": doc.get("title", ""), "text": doc.get("text", "")}
# print(f"✅ Corpus loaded. {len(corpus)} documents.\n")

# # Initialize FastAPI
# app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Request and Response Models
# class QueryRequest(BaseModel):
#     text: str

# class ResponseModel(BaseModel):
#     answer: str

# # =====================================
# # ✨ Helper Functions
# # =====================================

# def chunk_text(text, max_tokens=1500):
#     words = text.split()
#     return [' '.join(words[i:i+max_tokens]) for i in range(0, len(words), max_tokens)]

# def quick_summarize_clean(texts, query_text, max_sentences=3, max_words=100):
#     sentences = []
#     for text in texts:
#         text_sentences = text.replace("\n", " ").split('。')
#         sentences.extend(text_sentences)

#     sentences = [s.strip() for s in sentences if len(s.strip()) > 5 and len(s.strip()) < 80]

#     if not sentences:
#         return ""

#     sentence_embeddings = compressor_model.encode(sentences, convert_to_tensor=True)
#     query_embedding = compressor_model.encode([query_text], convert_to_tensor=True)

#     cosine_scores = util.cos_sim(query_embedding, sentence_embeddings)[0]
#     top_results = torch.topk(cosine_scores, k=min(max_sentences, len(sentences)))

#     selected_sentences = [sentences[i] for i in top_results.indices]
#     summarized_text = "。".join(selected_sentences)

#     if len(summarized_text.split()) > max_words:
#         summarized_text = " ".join(summarized_text.split()[:max_words]) + "..."

#     return summarized_text

# def clean_user_text(user_text, max_sentences=10):
#     sentences = user_text.replace('\n', '').replace('\r', '').split('。')
#     sentences = [s.strip() for s in sentences if s.strip()]
#     keywords = ["梦见", "意味着", "预示", "暗示", "象征", "表明", "反映", "代表"]
#     filtered_sentences = [s for s in sentences if any(k in s for k in keywords)]

#     if not filtered_sentences:
#         filtered_sentences = sentences[:max_sentences]

#     return "。".join(filtered_sentences[:max_sentences])

# def detect_language(text):
#     for ch in text:
#         if '\u4e00' <= ch <= '\u9fff':
#             return "zh"
#     return "en"

# fallback_sci_zh = "根据弗洛伊德的梦的解析理论，梦境是潜意识欲望的表现，反映了内心未满足的需求和情感冲突。"
# fallback_sci_en = "According to Freud's theory of dream interpretation, dreams represent unconscious desires and reflect hidden emotional conflicts."

# # =====================================
# # ✨ Main Analyze Endpoint
# # =====================================

# @app.post("/analyze", response_model=ResponseModel)
# async def analyze_dream(request: QueryRequest):
#     try:
#         user_text = request.text

#         # Step 1: Clean user input
#         user_text = clean_user_text(user_text)

#         # Step 2: Search Corpus
#         query = {"q1": user_text}
#         results = retriever.search(query, top_k=20)

#         folk_contents = []
#         sci_contents = []

#         for doc_id, score in results["q1"].items():
#             if doc_id in corpus:
#                 if doc_id.startswith("PMC"):
#                     if len(sci_contents) < 3:
#                         sci_contents.append(corpus[doc_id]["text"])
#                 else:
#                     if len(folk_contents) < 5:
#                         folk_contents.append(corpus[doc_id]["text"])
#             if len(folk_contents) >= 5 and len(sci_contents) >= 3:
#                 break

#         # Step 3: Summarize & Clean
#         summarized_folk = quick_summarize_clean(folk_contents, user_text)
#         summarized_sci = quick_summarize_clean(sci_contents, user_text)

#         user_lang = detect_language(user_text)

#         # Step 4: Fallback if necessary
#         if not summarized_sci or len(summarized_sci) < 30:
#             summarized_sci = fallback_sci_zh if user_lang == "zh" else fallback_sci_en

#         # Step 5: Build Prompt
#         if user_lang == "zh":
#             prompt = f"""
# 你是一位经验丰富的梦境分析师。

# 请根据以下内容，撰写连贯自然的梦境解析，分为以下三部分：

# [梦境象征意义]
# {summarized_folk}

# [科学文献支持]
# {summarized_sci}

# [总结用户的心理状态与建议]
# 结合梦境象征与科学理论，推测用户的心理状态变化，给出积极温暖的建议。

# 要求：
# - 用中文回答
# - 结构清晰，逻辑自然
# - 总字数控制在600-800字
# """
#         else:
#             prompt = f"""
# You are an experienced dream analyst.

# Based on the content below, write a coherent and natural dream analysis structured into three sections:

# [Dream Symbolism Interpretation]
# {summarized_folk}

# [Scientific Literature Support]
# {summarized_sci}

# [Summary and Psychological Analysis]
# Integrate symbolism and science to infer the user's psychological state and offer warm, supportive advice.

# Requirements:
# - Write in English
# - Structure clearly, naturally
# - Limit total length to 600-800 words
# """

#         # Step 6: LLM Generation
#         chunks = chunk_text(prompt, max_tokens=1500)
#         final_answer_parts = []

#         for chunk in chunks:
#             input_ids = tokenizer(chunk, return_tensors="pt", truncation=True, padding=True, max_length=2048).input_ids.to(device)
#             output_ids = model.generate(
#                 input_ids,
#                 max_new_tokens=400,
#                 temperature=0.7,
#                 pad_token_id=tokenizer.eos_token_id
#             )
#             answer = tokenizer.decode(output_ids[0], skip_special_tokens=True)
#             final_answer_parts.append(answer)

#         final_answer = "\n".join(final_answer_parts)

#         return {"answer": final_answer}

#     except Exception as e:
#         import traceback
#         print("🔥 Error occurred:", str(e))
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=str(e))

# # Launch server
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=False)

















# ✅ backend/main.py

import sys
import os
import json
import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import hf_hub_download
from sentence_transformers import SentenceTransformer, util
from langdetect import detect

# Disable Hugging Face symlink warning
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TRANSFORMERS_NO_TF"] = "1"

# Set path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from retriever.retriever import MemmapRetriever

# Load small compressor model
compressor_model = SentenceTransformer("all-MiniLM-L6-v2")

# Auto device
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"\n🔥 Using device: {device}")

# Load DeepSeek
print("🔄 Loading DeepSeek model...")
tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B")
model = AutoModelForCausalLM.from_pretrained(
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
    torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    trust_remote_code=True
).to(device)
print("✅ DeepSeek model loaded.\n")

# Load Retriever
print("🔄 Loading Retriever...")
retriever = MemmapRetriever(
    memmap_path="retriever/corpus_emb.dat",
    doc_ids_path="retriever/corpus_doc_ids.json",
    dimension=384,
    num_docs=len(json.load(open("retriever/corpus_doc_ids.json"))),
    model_name="Lajavaness/bilingual-embedding-small"
)
print("✅ Retriever loaded.\n")

# Load corpus
print("🔄 Downloading corpus.jsonl...")
corpus_path = hf_hub_download(
    repo_id="COMP631GroupSYCZ/Corpus",
    filename="corpus.jsonl",
    repo_type="dataset",
    cache_dir="retriever/hf_cache"
)

print("🔄 Loading corpus...")
corpus = {}
with open(corpus_path, "r", encoding="utf-8") as f:
    for line in f:
        doc = json.loads(line.strip())
        doc_id = doc["_id"]
        corpus[doc_id] = {"title": doc.get("title", ""), "text": doc.get("text", "")}
print(f"✅ Corpus loaded. {len(corpus)} documents.\n")

# FastAPI
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class QueryRequest(BaseModel):
    text: str
    deep_thinking: bool = False

class ResponseModel(BaseModel):
    answer: str

# Helper Functions
def quick_summarize_clean(texts, query_text, max_sentences=3):
    sentences = []
    for text in texts:
        text_sentences = text.replace("\n", " ").split('。')
        sentences.extend(text_sentences)

    sentences = [s.strip() for s in sentences if len(s.strip()) > 5 and len(s.strip()) < 80]

    if not sentences:
        return ""

    sentence_embeddings = compressor_model.encode(sentences, convert_to_tensor=True)
    query_embedding = compressor_model.encode([query_text], convert_to_tensor=True)

    cosine_scores = util.cos_sim(query_embedding, sentence_embeddings)[0]
    top_results = torch.topk(cosine_scores, k=min(max_sentences, len(sentences)))

    selected_sentences = [sentences[i] for i in top_results.indices]
    summarized_text = "。".join(selected_sentences)
    return summarized_text

def detect_language(text):
    try:
        lang = detect(text)    # returns 'zh-cn','en','es','fr', etc.
    except:
        lang = 'en'
    return lang
    
fallback_sci_zh = "根据弗洛伊德的梦的解析理论，梦境是潜意识欲望的表现，反映了内心未满足的需求和情感冲突。"
fallback_sci_en = "According to Freud's theory of dream interpretation, dreams represent unconscious desires and reflect hidden emotional conflicts."

# Endpoint
@app.post("/analyze", response_model=ResponseModel)
async def analyze_dream(request: QueryRequest):
    try:
        user_text = request.text
        # Always respond in the user's input language
        lang = detect_language(user_text)

        # 1. Retrieval
        query = {"q1": user_text}
        results = retriever.search(query, top_k=20)
        folk_contents, sci_contents = [], []
        for doc_id, _ in results.get("q1", {}).items():
            if doc_id in corpus:
                if doc_id.startswith("PMC") and len(sci_contents) < 3:
                    sci_contents.append(corpus[doc_id]["text"])
                elif not doc_id.startswith("PMC") and len(folk_contents) < 5:
                    folk_contents.append(corpus[doc_id]["text"])
            if len(folk_contents) >= 5 and len(sci_contents) >= 3:
                break

        # 2. Summarization
        summarized_folk = quick_summarize_clean(folk_contents, user_text)
        summarized_sci  = quick_summarize_clean(sci_contents, user_text)
        if not summarized_sci or len(summarized_sci) < 30:
            summarized_sci = fallback_sci_zh if lang.startswith("zh") else fallback_sci_en

        # 3. Prompt
        if lang.startswith("zh"):
            prompt = f"""
                    你是一位富有同理心且经验丰富的梦境分析师。
                    请以第一人称“我”温暖亲切的口吻并称呼对方为您，为客户撰写连贯且易懂的梦境解析，结构请严格按照以下格式进行编写：
                    
                    亲爱的用户您好，以下是您的梦境分析:
                    1. 梦境象征意义：
                       - {summarized_folk}
                       - 结合日常生活与心理学视角说明其可能反映的情感与需求
                    
                    2. 科学文献支持：
                       - {summarized_sci}
                       - 说明它们如何验证上述象征意义
                    
                    3. 心理状态总结与建议：
                       - 概括客户当前的心理状态
                       - 提供2–3条实际可行的温馨建议
                    
                    要求：
                    - 必须以“梦境分析”标题开头
                    - 严格输出上述三部分，不要多余说明
                    - 语言自然连贯
                    """
        else:
            prompt = f"""
                    You are an empathetic and skilled dream analyst. Read the client’s dream context below and respond warmly in the first person (“I”) and treat the client as "You", please strictly following this exact structure:
                    
                    Dear Client, Here is the Dream Analysis for you:
                    
                    1. Dream Symbolism Interpretation:
                       - {summarized_folk}
                       - Explain what each symbol might reveal about the client’s emotions or life circumstances.
                    
                    2. Scientific Literature Support:
                       - {summarized_sci}
                       - Briefly explain how they validate your symbolism interpretation.
                    
                    3. Psychological Summary & Practical Advice:
                       - Summarize the client’s probable mental state.
                       - Offer 2–3 warm, actionable suggestions for reflection or coping.
                    
                    Requirements:
                    - Output must start with “Dream Analysis:”
                    - Only include the three sections above—no extra narrative or prompt text
                    - Write in fluent, supportive English with varied sentence structure
                    """

        # 4. Generate
        input_ids = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=2048
        ).input_ids.to(device)
        output_ids = model.generate(
            input_ids,
            max_new_tokens=600,
            temperature=0.7,
            pad_token_id=tokenizer.eos_token_id
        )

        # 5. Extract only the generated part
        gen_ids     = output_ids[0][ input_ids.shape[-1] : ]
        raw_answer  = tokenizer.decode(gen_ids, skip_special_tokens=True)

        # 6. Trim anything before our header
        clean_answer = re.sub(r'^<think>.*?<think>', '', raw_answer, flags=re.DOTALL).strip()

        return {"answer": clean_answer}

    except Exception as e:
        import traceback
        print("🔥 Error occurred:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}

# Run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=False)
