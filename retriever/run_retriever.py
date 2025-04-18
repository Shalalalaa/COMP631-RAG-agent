from retriever import MemmapRetriever
import json

if __name__ == '__main__':
    memmap_path = "corpus_emb.dat"
    doc_ids_path = "corpus_doc_ids.json"
    model_name = "Lajavaness/bilingual-embedding-small"

    retriever = MemmapRetriever(
        memmap_path=memmap_path,
        doc_ids_path=doc_ids_path,
        dimension=384,
        num_docs=len(json.load(open(doc_ids_path))),
        model_name=model_name
    )

    queries = {
        "q1": "我昨晚梦见飞翔的鱼和奇怪的建筑，想了解这两个梦境的意义。"
    }
    results = retriever.search(queries, top_k=5)
    print(json.dumps(results, ensure_ascii=False, indent=2))

    # 检索完成后，拿到 results
    results = retriever.search(queries, top_k=3)

    # 加载原 corpus（原文档内容）
    # corpus, _, _ = load_corpus(
    #     repo_id="COMP631GroupSYCZ/Corpus",
    #     filename="corpus.jsonl"
    # )
    corpus, _ = load_corpus(
        repo_id="COMP631GroupSYCZ/Corpus",
        filename="corpus.jsonl"
    )

    # 把结果根据 doc_id还原成 文本内容
    for query_id, doc_scores in results.items():
        print(f"🔍 查询: {query_id}")
        for doc_id, score in doc_scores.items():
            text = corpus[str(doc_id)]['text'][:200]  # 只打印前200字符
            print(f"📄 文档ID: {doc_id}, 相似度: {score:.4f}")
            print(f"内容: {text}")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")