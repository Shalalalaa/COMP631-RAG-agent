import os
import json
import pandas as pd

base_dir = "data/ZhouGong"

data_list = []
file_id = 1  

for category in os.listdir(base_dir):
    category_path = os.path.join(base_dir, category)
    
    if os.path.isdir(category_path):
        for filename in os.listdir(category_path):
            if filename.endswith(".json"):
                file_path = os.path.join(category_path, filename)
                
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        json_data = json.load(f)
                        text = json_data.get("content", "").strip()
                        
                        title = filename.replace(".json", "")
                        
                        data_list.append({
                            "id": file_id,
                            "title": title,
                            "text": text
                        })
                        print(f"✅ Successfully convert: {file_path}")
                        file_id += 1
                except Exception as e:
                    print(f"❌ Failed when read {file_path}: {e}")

df = pd.DataFrame(data_list)
csv_path = "zhougong_corpus.csv"
df.to_csv(csv_path, index=False, encoding="utf-8-sig")

print(f"\n📂 Corpus CSV saved to: {csv_path}")
