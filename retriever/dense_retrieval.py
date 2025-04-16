# dense_retrieval.py

import torch
from sentence_transformers import util

class DenseRetrievalExactSearch:
    def __init__(self, text_embedding_model, batch_size=32, corpus_size=None):
        """
        text_embedding_model: SentenceTransformer 模型
        batch_size: 批量计算大小
        corpus_size: 限制索引文档数量（用于测试）
        """
        self.model = text_embedding_model
        self.batch_size = batch_size
        self.corpus_size = corpus_size
        self.corpus_embeddings = None
        self.doc_ids = None

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

        # 批量计算嵌入向量
        print("🔍 正在计算嵌入向量...")
        all_embeddings = []
        for i in range(0, len(docs), self.batch_size):
            batch = docs[i:i + self.batch_size]
            emb = self.model.encode(batch, convert_to_tensor=True)
            all_embeddings.append(emb)

        self.corpus_embeddings = torch.cat(all_embeddings, dim=0)
        print(f"✅ 嵌入完成，共索引文档数: {len(self.doc_ids)}")

    def search(self, query, top_k=5, score_function='cos_sim'):
        """
        query: str 查询文本
        return: [(doc_id, score)]
        """
        query_embedding = self.model.encode(query, convert_to_tensor=True)

        if score_function == 'cos_sim':
            sim_scores = util.cos_sim(query_embedding, self.corpus_embeddings)[0]
        elif score_function == 'dot':
            sim_scores = torch.matmul(query_embedding, self.corpus_embeddings.T)[0]
        else:
            raise ValueError(f"不支持的 score_function: {score_function}")

        top_results = torch.topk(sim_scores, k=top_k)
        return [(self.doc_ids[idx], sim_scores[idx].item()) for idx in top_results.indices]
