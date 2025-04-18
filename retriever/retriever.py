# retriever/retriever.py
import os
import json
import numpy as np
import torch
from sentence_transformers import SentenceTransformer, util

class MemmapRetriever:
    def __init__(self, memmap_path, doc_ids_path, dimension, num_docs, model_name):
        self.dimension = dimension
        self.num_docs = num_docs
        self.mmap = np.memmap(memmap_path, dtype='float32', mode='r', shape=(num_docs, dimension))
        self.corpus_embeddings = torch.from_numpy(self.mmap)
        with open(doc_ids_path, 'r', encoding='utf-8') as f:
            self.doc_ids = json.load(f)
        self.model = SentenceTransformer(model_name, trust_remote_code=True)

    def search(self, queries: dict, top_k: int = 5, score_function: str = 'cos_sim'):
        query_ids = list(queries.keys())
        query_texts = [queries[q] for q in query_ids]
        query_emb = self.model.encode(
            query_texts,
            convert_to_tensor=True,
            batch_size=32,
            max_length=512,
            truncation=True
        ).to('cpu')

        if score_function == 'cos_sim':
            sim = util.cos_sim(query_emb, self.corpus_embeddings)
        elif score_function == 'dot':
            sim = torch.matmul(query_emb, self.corpus_embeddings.T)
        else:
            raise ValueError(f"Unsupported score_function {score_function}")

        results = {}
        for idx, qid in enumerate(query_ids):
            topk = torch.topk(sim[idx], k=top_k)
            ids, scores = topk.indices.tolist(), topk.values.tolist()
            results[qid] = {self.doc_ids[i]: s for i, s in zip(ids, scores)}
        return results
