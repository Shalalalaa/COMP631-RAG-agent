# 如果还没有安装相关依赖，可以先执行下面的安装命令（只需执行一次）
# !pip install sentence-transformers huggingface_hub transformers

import json
import torch
import os
from sentence_transformers import SentenceTransformer, util
from huggingface_hub import hf_hub_download

# ✅ 是否启用情绪辅助功能（设置为 False 可禁用）
USE_EMOTION_ASSIST = True

# ------------------------------
# 定义 DenseRetrievalExactSearch 类（支持向量存储）
# ------------------------------
class DenseRetrievalExactSearch:
    def __init__(self, text_embedding_model, batch_size=32, corpus_size=None, save_path="corpus_data"):
        """
        text_embedding_model: SentenceTransformer 模型
        batch_size: 批量计算大小
        corpus_size: 限制索引文档数量（用于测试）
        save_path: 存储嵌入向量的文件夹
        """
        self.model = text_embedding_model
        self.batch_size = batch_size
        self.corpus_size = corpus_size
        self.corpus_embeddings = None
        self.doc_ids = None
        self.save_path = save_path
        os.makedirs(save_path, exist_ok=True)  # 确保目录存在

    def index_corpus(self, corpus):
        """
        corpus: 字典，格式 { doc_id: { "title": 文本 } }
        """
        self.doc_ids = list(corpus.keys())
        docs = [corpus[doc_id]["title"] for doc_id in self.doc_ids]

        # 限制 corpus_size
        if self.corpus_size is not None:
            docs = docs[:self.corpus_size]
            self.doc_ids = self.doc_ids[:self.corpus_size]

        # **检查是否已存储嵌入**
        emb_path = os.path.join(self.save_path, "corpus_embeddings.pt")
        doc_path = os.path.join(self.save_path, "corpus_doc_ids.json")

        if os.path.exists(emb_path) and os.path.exists(doc_path):
            print("✅ 加载已存储的嵌入向量...")
            self.corpus_embeddings = torch.load(emb_path)
            with open(doc_path, "r") as f:
                self.doc_ids = json.load(f)
            print(f"✅ 加载完成: {len(self.doc_ids)} 文档")
            return

        # **嵌入未存储，计算嵌入**
        print("🔄 计算文档嵌入...")
        batch_size = self.batch_size
        all_embeddings = []
        for i in range(0, len(docs), batch_size):
            batch_docs = docs[i : i + batch_size]
            batch_embeddings = self.model.encode(batch_docs, convert_to_tensor=True)
            all_embeddings.append(batch_embeddings)

        # **合并所有批次**
        self.corpus_embeddings = torch.cat(all_embeddings, dim=0)
        print(f"✅ 文档嵌入计算完成: {len(self.doc_ids)} 文档")

        # **存储到磁盘**
        torch.save(self.corpus_embeddings, emb_path)
        with open(doc_path, "w") as f:
            json.dump(self.doc_ids, f)
        print("✅ 嵌入向量已保存，下次可直接加载！")

    def search(self, corpus, queries, top_k=5, score_function='dot', return_sorted=True):
        """
        corpus: { doc_id: { "title": 文本 } }
        queries: { query_id: 查询文本 }
        top_k: 返回前 k 个相似文档
        score_function: 'cos_sim' 或 'dot'
        """
        # **确保已加载嵌入**
        if self.corpus_embeddings is None:
            self.index_corpus(corpus)

        # **计算查询向量**
        query_ids = list(queries.keys())
        query_texts = [queries[qid] for qid in query_ids]
        query_embeddings = self.model.encode(query_texts, batch_size=self.batch_size, convert_to_tensor=True)

        # **计算相似度**
        if score_function == 'cos_sim':
            sim_matrix = util.cos_sim(query_embeddings, self.corpus_embeddings)
        elif score_function == 'dot':
            sim_matrix = torch.matmul(query_embeddings, self.corpus_embeddings.T)
        else:
            raise ValueError(f"❌ 不支持的 score_function: {score_function}")

        # **获取 top-k 结果**
        results = {}
        for i, qid in enumerate(query_ids):
            sims = sim_matrix[i]
            top_results = torch.topk(sims, k=top_k)
            top_indices = top_results.indices
            top_scores = top_results.values

            result = {self.doc_ids[idx]: score.item() for idx, score in zip(top_indices, top_scores)}
            results[qid] = result

        return results


# ------------------------------
# 下载并加载语料（corpus.jsonl）
# 这里假设你的语料上传在 Hugging Face 的仓库 "COMP631GroupSYCZ/Corpus"，文件名为 "corpus.jsonl"
# ------------------------------
print("Downloading corpus from Hugging Face ...")
corpus_path = hf_hub_download(repo_id="COMP631GroupSYCZ/Corpus",
                              filename="corpus.jsonl",
                              repo_type="dataset")
print("Corpus downloaded:", corpus_path)

# 读取 JSONL 文件，每行解析为一个 JSON 对象，并构造成 { doc_id: {"title": 文本 } } 的格式
corpus = {}
with open(corpus_path, 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            doc = json.loads(line)
            doc_id = doc["_id"]
            corpus[doc_id] = {"title": doc["title"]}

print("Total documents loaded:", len(corpus))

# # 打印 corpus 最后 7 条数据的 ID 和标题
# for doc_id in list(corpus.keys())[-7:]:
#     print(f"ID: {doc_id}")
#     print(f"Title: {corpus[doc_id].get('title', 'No title')}\n")

# ------------------------------
# 加载文本嵌入模型
# ------------------------------
print("Loading text embedding model ...")
model = SentenceTransformer("Lajavaness/bilingual-embedding-small", trust_remote_code=True)
print("Model loaded.")

# ✅ 如果启用情绪辅助，则加载情绪识别模型
if USE_EMOTION_ASSIST:
    from transformers import pipeline
    emotion_model = pipeline("text-classification", model="nateraw/bert-base-uncased-emotion", return_all_scores=True)
    print("Emotion model loaded.\n")

# ------------------------------
# 初始化三个 Retriever
# ------------------------------
corpus_sci = {}
corpus_folk = {}
corpus_freud = {}

for doc_id, content in corpus.items():
    if doc_id.startswith("PMC"):
        corpus_sci[doc_id] = content
    elif doc_id.startswith("doc3_"):
        corpus_freud[doc_id] = content
    elif doc_id.isdigit():
        corpus_folk[doc_id] = content

print(f"✅ 科学文献数量: {len(corpus_sci)}")
print(f"✅ 周公解梦数量: {len(corpus_folk)}")
print(f"✅ 弗洛伊德内容数量: {len(corpus_freud)}\n")

retriever_sci = DenseRetrievalExactSearch(model, save_path="retriever_sci")
retriever_folk = DenseRetrievalExactSearch(model, save_path="retriever_folk")
retriever_freud = DenseRetrievalExactSearch(model, save_path="retriever_freud")

retriever_sci.index_corpus(corpus_sci)
retriever_folk.index_corpus(corpus_folk)
retriever_freud.index_corpus(corpus_freud)


# ------------------------------
# 定义情绪+语义融合检索的函数
# ------------------------------
def hybrid_emotion_search(dream_text, top_k=5, alpha=0.7):
    """
    将dream_text与提取到的情绪标签一起，用加权向量融合检索corpus_sci。
    """
    # 1. 原始梦境向量
    v_semantic = model.encode(dream_text, convert_to_tensor=True)

    # 2. 情绪标签
    emotion_results = emotion_model(dream_text)[0]  # list of dict: {'label':..., 'score':...}
    top_tags = [r['label'] for r in sorted(emotion_results, key=lambda x: x['score'], reverse=True)[:2]]
    # 构造一个情绪查询字符串
    emotion_query = "dream, " + ", ".join(top_tags)
    v_emotion = model.encode(emotion_query, convert_to_tensor=True)

    # 3. 向量融合
    v_query = alpha * v_semantic + (1 - alpha) * v_emotion

    # 4. 和科学文献 embeddings 做cosine相似度
    sim_matrix = util.cos_sim(v_query, retriever_sci.corpus_embeddings)[0]
    top_indices = torch.topk(sim_matrix, k=top_k).indices

    # 5. 生成结果
    results = {}
    for i in top_indices:
        doc_id = retriever_sci.doc_ids[i]
        results[doc_id] = sim_matrix[i].item()

    return results, top_tags


# ------------------------------
# 现在准备查询
# ------------------------------
user_query = {
    "q1": "我昨晚梦见飞翔的鱼和奇怪的建筑",
    "q2": "Freudian dream analysis about symbols and hidden desires",  # 示例英文查询
    "q3": "I was surrounded by a mass of people, some of whom I knew and some I didn't know. The dream continued like that for what seemed to be a long time. The people were not talking or moving. They were just existing. I was not talking or moving. We were all just standing there. The background was just all darkness with, no dimension. It was as if we were floating on nothing, existing nowhere. The people were of every race, sex and age. Then, after a while, everyone, but me, just fell in the darkness, tumbling down until they became very small, then they disappeared. They did not scream or make any noise. I was left alone, but did not wonder where everyone left, until I woke up a few minutes later. I don't recall having any feelings during the dream. The dream was not pleasant or unpleasant. It kind if just happened. (153 words)",
    "q4": "I felt scared. I was pregnant in my dream. Then the dream jumped to my boyfriend and we're having sex together when his parents come home early from their vacation and caught us. I started to cry and his mom comforted me. She kept saying It's OK sweetheart. His father took him aside and talked with him. I was so embarrassed. What would they think of me now? Would they hate me? They loved me once. In real life I know this would never have happened. His parents would kill us instead.",
    "q5": "I feel anxiety, what should I do",
}

if USE_EMOTION_ASSIST:
    # ✅ 使用情绪辅助+语义融合检索
    results_sci = {}
    for qid, text in user_query.items():
        r, tags = hybrid_emotion_search(text, top_k=3, alpha=0.7)
        results_sci[qid] = r
        print(f"【情绪辅助】Query: {text}")
        print(f"Detected Emotions: {tags}\n")
else:
    # ❌ 不使用情绪辅助时，原生检索
    results_sci = retriever_sci.search(corpus_sci, user_query, top_k=3, score_function='cos_sim')

# 周公解梦和弗洛伊德依旧使用普通检索
results_folk = retriever_folk.search(corpus_folk, user_query, top_k=3, score_function='cos_sim')
results_freud = retriever_freud.search(corpus_freud, user_query, top_k=3, score_function='cos_sim')


# ------------------------------
# 打印查询结果
# ------------------------------
def print_query_results(user_query, sci_results, folk_results, freud_results, corpus_sci, corpus_folk, corpus_freud):
    print("💤 用户输入梦境：", user_query["q3"])
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # ─────────────────────────────
    print("🔮 【民俗解读】")
    folk = folk_results.get("q3", {})
    if folk:
        for doc_id, score in folk.items():
            title = corpus_folk[doc_id].get("title", "")[:80]
            print(f"🔸 {title} (Score: {score:.4f})")
    else:
        print("⚠️ 暂无相关的周公解梦匹配结果")
    print()

    # ─────────────────────────────
    print("🧠 【精神分析视角】")
    freud = freud_results.get("q3", {})
    if freud:
        for doc_id, score in freud.items():
            title = corpus_freud[doc_id].get("title", "")[:80]
            print(f"🔹 {title} (Score: {score:.4f})")
    else:
        print("⚠️ 暂无弗洛伊德理论相关解释")
    print()

    # ─────────────────────────────
    print("🔬 【科学解释】")
    sci = sci_results.get("q3", {})
    if sci:
        for doc_id, score in sci.items():
            title = corpus_sci[doc_id].get("title", "")[:80]
            print(f"🔬 {title} (Score: {score:.4f})")
    else:
        print("⚠️ 未找到匹配的心理学研究文献")
    print()

    # ─────────────────────────────
    print("📝 【情绪分析与建议】（可在此处添加更多基于情绪的个性化建议）")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

print_query_results(user_query, results_sci, results_folk, results_freud, corpus_sci, corpus_folk, corpus_freud)
