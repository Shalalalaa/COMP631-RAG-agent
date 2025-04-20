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

def detect_language(text: str) -> str:
    if any('\u4e00' <= ch <= '\u9fff' for ch in text):
        return 'zh'
    try:
        return detect(text)  # 'en', 'es', 'fr', ...
    except Exception:
        return 'en'
    
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
                    你是一位资深梦境分析师。请严格遵守以下规则：
                    
                    输出必须紧扣用户梦境描述：{user_text}
                    A. 仅在 <response> 与 </response> 之间输出一次正文；禁止出现 <think>、Markdown、代码块、星号或任何其他标签。  
                    B. 回复必须为中文，总字数≤500字。  
                    C. 必须完整保留模板行次序，不得增删标题或行。  
                    D. 输出完毕后立即打印单独一行“### END”。
                    E. 全程称呼用户为“您”，不得出现“客服”，“我们”或是“我”等其他称谓。
                    F. 解释与建议必须引用或呼应用户梦境描述中的元素，避免空泛套话。
                    G. 请确保全片内容都是中文
                    
                    <response>
                    亲爱的用户您好，以下是您的梦境分析:
                    1. 梦境象征意义：{summarized_folk}
                       - 请结合“{user_text}”等关键细节，说明上述意象与情绪或需求的联系。
                       - 如果{summarized_folk}中的内容与{user_text}不相关可以忽略
                       - 如果{summarized_folk}中的内容不是中文，请将其翻译成中文
                    2. 科学文献支持：{summarized_sci}
                       - 简述研究如何印证第1点，并引用梦境中的元素佐证，如果{summarized_sci}中的内容与{user_text}不相关可以忽略。
                       - 如果{summarized_sci}中的内容不是中文，请将其翻译成中文
                    3. 心理状态总结与建议：
                       - 概括您当前可能的心理状态。
                       - 建议1：____，建议理由：____
                       - 建议2：____，建议理由：____
                    </response>
                    ### END
                    """
            
        elif lang.startswith("en"):
            prompt = f"""
                    You are an experienced dream analyst. Follow ALL rules below:
                    
                    ① Read the client's dream description first: {user_text}
                    A. Write ONLY once inside <response> and </response>. Do NOT output <think>, Markdown, code fences, asterisks or extra tags.  
                    B. The reply must be in English and ≤ 800 words.  
                    C. Keep the exact template. Do not add or remove headings or lines.  
                    D. Stop after printing the single line “### END”.
                    E. Address the client consistently as “You”; do not use any other pronouns or roles.
                    F. All interpretations and advice must explicitly reference the client’s dream description; avoid generic wording.
                    G. Must return English
                    
                    <response>
                    Dear Client, here is your Dream Analysis:
                    1. Dream Symbolism Interpretation: {summarized_folk}
                       - Use Jungian symbolism or cognitive dream theory to relate the imagery to key details from the dream such as “{user_text}”, explaining what it may reveal about emotions or unmet needs.
                       - If{summarized_folk}is not related to {user_text}, ignore it.
                       - If{summarized_folk}is not English, then translate it to English.
                    2. Scientific Literature Support: {summarized_sci}
                       - Briefly state how the cited research corroborates the symbolism interpretation and connect it to specific elements of the dream.
                       - If{summarized_sci}is not related to {user_text}, ignore it.
                       - If{summarized_sci}is not English, then translate it to English.
                    3. Psychological Summary & Advice:
                       - Concisely summarise your likely psychological state (must reflect the dream content).
                       - Advice 1: ____ , Reason: ____
                       - Advice 2: ____ , Reason: ____
                    </response>
                    ### END
                    """
            
        # 4. Generate
        
        enc = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            padding=True,          # left‑pads to the longest sequence in the batch
            max_length=2048
        )
        
        input_ids      = enc["input_ids"].to(device)
        attention_mask = enc["attention_mask"].to(device)
        
        # ─── Ensure PAD token is defined and distinct from EOS ───────────────────────
        if tokenizer.pad_token_id is None:
            # add a new PAD token if the model / tokenizer doesn't have one
            tokenizer.add_special_tokens({'pad_token': '[PAD]'})
            model.resize_token_embeddings(len(tokenizer))
            model.config.pad_token_id = tokenizer.pad_token_id
        
        # ─── Generation hyper‑parameters ─────────────────────────────────────────────
        # choose a shorter cap for Chinese to stay inside the 500‑character limit
        max_tokens = 450 if lang.startswith("zh") else 950
        
        generation_args = dict(
            max_new_tokens=max_tokens,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.2,
            no_repeat_ngram_size=4,
            eos_token_id=[
                tokenizer.eos_token_id,                          # normal EOS
                tokenizer("\n### END").input_ids[-1]             # custom hard stop
            ],
            pad_token_id=tokenizer.pad_token_id
        )
        
        # ─── Generate ────────────────────────────────────────────────────────────────
        output_ids = model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,   # ★ pass the mask to avoid warning
            **generation_args
        )

        
            
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
            
        def extract_response(text):
            text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
            m = re.search(r"<response>(.*?)</response>", text, flags=re.S)
            if m:
                return m.group(1).strip()
            text = text.split("### END")[0]
            text = re.sub(r"<.*?>", "", text)
            return text.strip()
            
        raw_answer = tokenizer.decode(gen_ids, skip_special_tokens=True)
        clean_answer = extract_response(clean_output(raw_answer))

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
