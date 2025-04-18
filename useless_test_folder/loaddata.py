from datasets import load_dataset
from huggingface_hub import login

# token
login("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")

dataset = load_dataset("csv", data_files=["getResource/split_csvs/*.csv", "zhougong_corpus.csv"])

dataset.push_to_hub("siyihu/COMP631")

# dataset = load_dataset("siyihu/COMP631")
# print(dataset)
