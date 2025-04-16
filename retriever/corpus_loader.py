import json

def load_corpus(path):
    with open(path, 'r', encoding='utf-8') as f:
        return {json.loads(line)['_id']: {"title": json.loads(line)['title']} for line in f if line.strip()}

def split_corpus(corpus):
    sci = {k: v for k, v in corpus.items() if k.startswith("PMC")}
    folk = {k: v for k, v in corpus.items() if k.isdigit()}
    freud = {k: v for k, v in corpus.items() if k.startswith("doc3_")}
    return sci, folk, freud
