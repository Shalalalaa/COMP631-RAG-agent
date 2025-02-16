import requests
import json
import time

def get_open_access_papers(total_papers=100000, batch_size=1000):
    # extend the keyword search
    query = (
        "(psychology OR 'cognitive science' OR 'behavioral science' OR 'neuroscience' OR 'mental health' OR cognition) "
        "AND (dreams OR sleep OR consciousness OR therapy OR memory OR emotions) "
        "AND OPEN_ACCESS:Y"
    )

    base_url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    all_papers = []
    cursor_mark = "*"  

    while len(all_papers) < total_papers:
        remaining_papers = total_papers - len(all_papers)
        batch = min(batch_size, remaining_papers)

        params = {
            "query": query,
            "resultType": "core",
            "format": "json",
            "pageSize": batch,
            "cursorMark": cursor_mark
        }

        response = requests.get(base_url, params=params)
        data = response.json()

        results = data.get("resultList", {}).get("result", [])
        if not results:
            print("❌ There iiss no more articles.")
            break

        for paper in results:
            pmc_id = paper.get("pmcid", None)
            fulltext_url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc_id}/fullTextXML" if pmc_id else None

            all_papers.append({
                "title": paper.get("title", ""),
                "authors": paper.get("authorString", ""),
                "journal": paper.get("journalInfo", {}).get("title", ""),
                "pubYear": paper.get("pubYear", ""),
                "doi": paper.get("doi", ""),
                "abstract": paper.get("abstractText", ""),
                "fulltext_url": fulltext_url
            })

        cursor_mark = data.get("nextCursorMark", cursor_mark)
        print(f"✅ Already get {len(all_papers)} / {total_papers} article(s)...")

        time.sleep(1)

    # record into json fiile
    with open("open_access_papers.json", "w", encoding="utf-8") as f:
        json.dump(all_papers, f, ensure_ascii=False, indent=4)

    print(f"✅ Complete, found {len(all_papers)} open access articles, recorded to open_access_papers.json")

get_open_access_papers(total_papers=100000, batch_size=1000)
