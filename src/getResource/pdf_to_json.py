import os
import json
import fitz  # PyMuPDF
import concurrent.futures

PDF_DIR = "data/EuropePMC/PDFs"
OUTPUT_JSONL = "data/EuropePMC/extracted_papers.jsonl"
PROCESSED_LOG = "data/EuropePMC/processed_papers.json"

os.makedirs(os.path.dirname(OUTPUT_JSONL), exist_ok=True)

if os.path.exists(PROCESSED_LOG):
    with open(PROCESSED_LOG, "r", encoding="utf-8") as f:
        processed_papers = set(json.load(f))
else:
    processed_papers = set()

def extract_text_from_pdf(pdf_path):
    """ extract text """
    try:
        doc = fitz.open(pdf_path)
        text = "\n".join(page.get_text("text") for page in doc)
        return text if len(text) > 200 else None
    except Exception as e:
        print(f"⚠️ Fail: {pdf_path}，error: {e}")
        return None

def process_pdf(pdf_file):
    """ process pdf to json """
    pmcid = pdf_file.replace(".pdf", "")
    pdf_path = os.path.join(PDF_DIR, pdf_file)

    if pmcid in processed_papers:
        return None

    text = extract_text_from_pdf(pdf_path)
    if text:
        return {"pmcid": pmcid, "content": text}
    return None

def save_to_jsonl(data):
    """ add data to jsonl file """
    with open(OUTPUT_JSONL, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

pdf_files = [f for f in os.listdir(PDF_DIR) if f.endswith(".pdf")]

# **use  multi core to do this PDF**
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    for result in executor.map(process_pdf, pdf_files):
        if result:
            save_to_jsonl(result)
            processed_papers.add(result["pmcid"])
            print(f"✅ Complet extract: {result['pmcid']}")

# record the handled pmcid
with open(PROCESSED_LOG, "w", encoding="utf-8") as f:
    json.dump(list(processed_papers), f, ensure_ascii=False, indent=4)

print(f"🎉 Complete, all finished `{OUTPUT_JSONL}`")
