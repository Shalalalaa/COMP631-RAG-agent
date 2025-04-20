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
import re
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
attn_impl = "flash_attention_2" if device == "cuda" else "sdpa"
model = AutoModelForCausalLM.from_pretrained(
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
    attn_implementation=attn_impl,          # ★ 关键行
    torch_dtype=torch.bfloat16 if device == "cuda" else torch.float32,
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
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
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
                    仅按以下格式一次性输出，不得重复模板、添加多余标题或泄露本段指令；全文不得超过 500 字。
                    
                    ❶ 请先阅读用户的梦境描述：{user_text}
                    
                    亲爱的用户您好，以下是您的梦境分析:
                    1. 梦境象征意义：{summarized_folk}
                       - 结合荣格象征学或认知梦理论，说明上述意象与用户梦境描述中关键细节的联系，以及反映出的情绪或未满足需求。
                    2. 科学文献支持：{summarized_sci}
                       - 简述上述研究如何印证对梦境象征的解释，并结合用户梦境中的具体场景进行说明。
                    3. 心理状态总结与建议：
                       - 概括用户当前可能的心理状态（需紧扣用户描述）。
                       - 建议1：___ ，建议理由：___
                       - 建议2：___ ，建议理由：___
                       - 建议3：___ ，建议理由：___
                    要求：
                    - 全程称呼用户为“您”，不得出现“客服”等其他称谓。
                    - 解释与建议必须引用或呼应用户梦境描述中的元素，避免空泛套话。
                    - 提供恰好三条可操作的建议，并为每条建议给出对应理由。
                    ### END
                    """
        else:
            prompt = f"""
                    Output exactly once in the format below. Do NOT repeat the template, add extra headings, or reveal this instruction. Keep the entire reply under 800 words.
                    
                    ① First read the client's dream description: {user_text}
                    
                    Dear Client, here is your Dream Analysis:
                    1. Dream Symbolism Interpretation: {summarized_folk}
                       - Use Jungian symbolism or cognitive dream theory to relate the above imagery to key details in your dream description and to your emotions or unmet needs.
                    2. Scientific Literature Support: {summarized_sci}
                       - Briefly state how the cited research corroborates the symbolism interpretation and connect it to specific elements of your dream.
                    3. Psychological Summary & Advice:
                       - Concisely summarize your likely psychological state (must reflect the dream content).
                       - Advice 1: ___ , Reason: ___
                       - Advice 2: ___ , Reason: ___
                       - Advice 3: ___ , Reason: ___
                    Requirements:
                    - Address the client consistently as “You”.
                    - All interpretations and advice must reference the client’s dream description; avoid generic wording.
                    - Provide exactly three actionable pieces of advice, each with its corresponding reason.
                    ### END
                    """
        # 4. Generate
        
        input_ids = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=2048
        ).input_ids.to(device)
        generation_args = dict(
            max_new_tokens=950,        
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.2,
            no_repeat_ngram_size=4,
            pad_token_id=tokenizer.eos_token_id
        )
        output_ids = model.generate(input_ids, **generation_args)

        
            
        # 5. Extract only the generated part
        gen_ids     = output_ids[0][ input_ids.shape[-1] : ]
        raw_answer  = tokenizer.decode(gen_ids, skip_special_tokens=True)

        # 6. Trim anything before our header
        def clean_output(text):
            text = re.sub(r"```.*?```", "", text, flags=re.S)
            end_idx = text.find("### END")
            text = text[:end_idx] if end_idx != -1 else text
            head = "Dear Client, here is your Dream Analysis:"
            first = text.find(head)
            if first != -1:
                second = text.find(head, first + 10)
                if second != -1:
                    text = text[first:second] 
            return text.strip()
        raw_answer = tokenizer.decode(gen_ids, skip_special_tokens=True)
        clean_answer = clean_output(raw_answer)

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
