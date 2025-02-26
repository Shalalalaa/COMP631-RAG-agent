import os
import json
import requests
import time

# ===================================
# download from the ID = "..."(record from last time stopped in europe_pmc_papers)
# ===================================
START_PMCID = "PMC11776255"


# Europe PMC API
BASE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

# the directories about PMC papers store location
DATA_DIR = "data/EuropePMC"
PDF_DIR = os.path.join(DATA_DIR, "PDFs")
PAPER_LIST_FILE = os.path.join(DATA_DIR, "europe_pmc_papers.json")
LOG_FILE = os.path.join(DATA_DIR, "downloaded_papers.json")

# make sure the directory exsist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

# get the list of the papers that already stored
if os.path.exists(PAPER_LIST_FILE):
    with open(PAPER_LIST_FILE, "r", encoding="utf-8") as f:
        stored_papers = json.load(f)
else:
    stored_papers = []
    

# get the list of the papers that already downloaded
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        downloaded_papers = set(json.load(f))
else:
    downloaded_papers = set()

# create paper dict avoid repeat
stored_paper_dict = {p["pmcid"]: p for p in stored_papers}

# make sure the condition
query = (
    "(psychology OR cognitive science OR behavioral science OR neuroscience OR mental health "
    "OR consciousness OR sleep OR dreams OR hypnosis OR meditation OR sleep disorders OR psychotherapy)"
    " AND OPEN_ACCESS:Y"
)

# Europe PMC get access of 120000 papers
page_size = 1000
cursor_mark = "*"
total_papers = 120000

# ===================================
# start from the point
# ===================================
start_index = 0
if START_PMCID:
    # search the index in stored_papers which is the same as START_PMCID
    for i, paper in enumerate(stored_papers):
        if paper["pmcid"] == START_PMCID:
            start_index = i
            break

print(f"⏩ From index {start_index} (PMCID = {stored_papers[start_index]['pmcid'] if stored_papers else 'N/A'}) start downloading...")


def get_open_access_papers():
    global cursor_mark
    new_papers = []

    while len(stored_paper_dict) < total_papers:
        params = {
            "query": query,
            "format": "json",
            "pageSize": page_size,
            "cursorMark": cursor_mark
        }

        response = requests.get(BASE_URL, params=params)
        if response.status_code != 200:
            print(f"⚠️ API request fail (Status code: {response.status_code})")
            break

        data = response.json()
        results = data.get("resultList", {}).get("result", [])
        if not results:
            print("❌ There is no more data！")
            break

        for paper in results:
            pmcid = paper.get("pmcid", None)
            title = paper.get("title", "NO TITLE")
            doi = paper.get("doi", "NO DOI")

            # skip  the repeat iid
            if not pmcid or pmcid in stored_paper_dict:
                continue

            pdf_url = f"https://europepmc.org/backend/ptpmcrender.fcgi?accid={pmcid}&blobtype=pdf"

            stored_paper_dict[pmcid] = {
                "pmcid": pmcid,
                "title": title,
                "doi": doi,
                "pdf_url": pdf_url
            }
            new_papers.append(stored_paper_dict[pmcid])

        cursor_mark = data.get("nextCursorMark", None)

        # store the data
        with open(PAPER_LIST_FILE, "w", encoding="utf-8") as f:
            json.dump(list(stored_paper_dict.values()), f, ensure_ascii=False, indent=4)

        print(f"✅ get access of {len(stored_paper_dict)} / {total_papers} papers...")

        time.sleep(1)

        if not cursor_mark:
            break

    print(f"🎉 Complete getting access! Total stored {len(stored_paper_dict)} papers to `{PAPER_LIST_FILE}`")
    return new_papers  # only return new added paper




def download_pdfs(papers, start_idx=0):
    """ start from the set ID"""
    for paper in papers[start_idx:]:
        pmcid = paper.get("pmcid")
        pdf_url = paper.get("pdf_url")
        pdf_filename = os.path.join(PDF_DIR, f"{pmcid}.pdf")

        if not pdf_url:
            print(f"⚠️ Skip {pmcid}, because pdf_url is empty")
            continue

        if os.path.exists(pdf_filename) and os.path.getsize(pdf_filename) > 1024:
            print(f"✅ Already downloaded, skip: {pdf_filename}")
            continue

        try:
            print(f"📥 Downloading: {pdf_url}")
            response = requests.get(pdf_url, stream=True)

            content_type = response.headers.get("Content-Type", "")
            if "application/pdf" not in content_type:
                print(f"⚠️ {pmcid} Download Failed: not a PDF type（{content_type}）")
                continue

            pdf_size = 0
            with open(pdf_filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        pdf_size += len(chunk)

            # if too small, file could be wrong
            if pdf_size < 1024:
                print(f"⚠️ {pmcid} Download Failed: the size of file is unusual with（{pdf_size} bytes）")
                os.remove(pdf_filename)
                continue

            print(f"✅ Download successfully: {pdf_filename} ({pdf_size} bytes)")

            # record the ID that downloaded
            downloaded_papers.add(pmcid)
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                json.dump(list(downloaded_papers), f, ensure_ascii=False, indent=4)

        except Exception as e:
            print(f"⚠️ Download Failed: {e}")

if os.path.exists(PAPER_LIST_FILE):
    print(f"📂 find the exist paper list `{PAPER_LIST_FILE}`，use directly...")
    with open(PAPER_LIST_FILE, "r", encoding="utf-8") as f:
        papers = json.load(f)
else:
    print("📥 didn't find paper list, getting it now...")
    papers = get_open_access_papers()


download_pdfs(papers, start_idx=start_index)
