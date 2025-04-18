import os
import json
import pandas as pd
import fitz
import pdfplumber  
import multiprocessing
import csv

# file path
json_path = "data/EuropePMC/europe_pmc_papers.json"
pdf_dir = "data/EuropePMC/PDFs"
csv_dir = "split_csvs"  
os.makedirs(csv_dir, exist_ok=True)  
max_length = 10000  
max_csv_size = 5000 * 1024 * 1024  
max_csv_rows = 1_000_000 
csv_path = os.path.join(csv_dir, "europe_pmc_1.csv")  
processed_ids_file = "processed_ids.txt"  


num_processes = min(multiprocessing.cpu_count(), 4)
print(f"🚀 use {num_processes} processors to analyze PDF")

# **read JSON and set `pmcid` -> `title` reflection
with open(json_path, "r", encoding="utf-8") as f:
    papers = json.load(f)
title_map = {paper["pmcid"]: paper["title"] for paper in papers}

log_file = "pdf_processing.log"

def log_message(message):
    """ record log """
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(message + "\n")
    print(message) 

# ewad the ids that already converted
def load_processed_ids():
    if os.path.exists(processed_ids_file):
        with open(processed_ids_file, "r", encoding="utf-8") as f:
            return set(f.read().splitlines()) 
    return set()

processed_ids = load_processed_ids() 

# **save the PDF ID that already converted**
def save_processed_id(pmcid):
    with open(processed_ids_file, "a", encoding="utf-8") as f:
        f.write(pmcid + "\n")

# **check if need new CSV**
def should_create_new_csv():
    """ if CSV file excceed 5GB or 1000k lines, create new file """
    global csv_path
    if not os.path.exists(csv_path):
        return False

    file_size = os.path.getsize(csv_path)
    row_count = sum(1 for _ in open(csv_path, "r", encoding="utf-8")) - 1  # calculate the lines

    return file_size > max_csv_size or row_count > max_csv_rows  # **if excced limitation return True**

# **check size of CSV，call after handled the PDF **
def check_csv_size():
    """ if file too big create new one """
    global csv_path
    if should_create_new_csv():
        csv_number = int(csv_path.split("_")[-1].split(".")[0]) + 1  # 计算下一个 CSV 编号
        csv_path = os.path.join(csv_dir, f"europe_pmc_{csv_number}.csv")
        log_message(f"📂 When CSV file is more than 5GB, create new file: {csv_path}")

# **save CSV**
def save_to_csv(data_list):
    """ save data to CSV """
    if not data_list:
        return
    
    check_csv_size()  # **check if need new CSV**
    df_new = pd.DataFrame(data_list)

    write_mode = "a" if os.path.exists(csv_path) else "w"
    header = not os.path.exists(csv_path) 

    try:
        df_new.to_csv(csv_path, mode=write_mode, index=False, encoding="utf-8-sig",
                      quoting=csv.QUOTE_ALL, escapechar="\\", header=header)
        log_message(f"\n💾 Saved {len(df_new)} data to {csv_path}")

    except Exception as e:
        log_message(f"❌ Failed to save CSV, error: {e}")

# **PDF convert**
def extract_text(pdf_path, pmcid):
    """ try use MuPDF, use pdfplumber after failed"""
    try:
        with fitz.open(pdf_path) as doc:
            text = " ".join([page.get_text("text") or "" for page in doc]).strip()
        if text:
            log_message(f"✅ MuPDF success: {pmcid} ({len(text)} bytes)")
            return text
    except Exception as e:
        log_message(f"⚠️ MuPDF fail {pmcid}, try pdfplumber: {e}")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = " ".join([page.extract_text() or "" for page in pdf.pages]).strip()
        if text:
            log_message(f"✅ pdfplumber success: {pmcid}({len(text)} bytes)")
            return text
    except Exception as e:
        log_message(f"❌ pdfplumber fail {pmcid}: {e}")

    return None  # **if two method failed, return None**

# **use multiple processor**
def process_pdf(pdf_file):
    """ convert one pdf and return the data """
    pmcid = os.path.splitext(pdf_file)[0]  # **get PDF ID（remove `.pdf` extend）**
    if pmcid in processed_ids:
        log_message(f"⏩ Skip: {pmcid}(Already converted)")
        return None  # **Skip the pdf files that already converted**

    pdf_path = os.path.join(pdf_dir, pdf_file)
    title = title_map.get(pmcid, "Unknown Title") 
    text = extract_text(pdf_path, pmcid)

    if not text:
        log_message(f"⚠️ Cannot convert: {pmcid}")
        return None
     # **save the already handled PDF**
    save_processed_id(pmcid) 
    
    if len(text) > max_length:
        chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
        log_message(f"⚠️ too long and cut it to several pieces: {pmcid}(total {len(chunks)} piece(s))")
        return [{"id": f"{pmcid}-{idx+1}", "title": title, "text": chunk} for idx, chunk in enumerate(chunks)]
    else:
        return [{"id": pmcid, "title": title, "text": text}]

if __name__ == "__main__":
    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith(".pdf")]

    data_list = []
    with multiprocessing.Pool(processes=num_processes) as pool:
        for idx, result in enumerate(pool.imap(process_pdf, pdf_files), 1):
            if result:
                data_list.extend(result)

            if len(data_list) >= 1000:
                save_to_csv(data_list)
                data_list = []

    if data_list:
        save_to_csv(data_list)

    log_message(f"\n📂 Complete all, stored in {csv_dir}")
