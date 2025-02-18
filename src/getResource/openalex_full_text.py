import requests
import json
import time
from io import BytesIO
import PyPDF2

# This list will store JSON objects containing PDF text and metadata
pdf_texts = []

# Define the base API endpoint and query parameters for OpenAlex.
# Only open access works will be returned.
base_url = "https://api.openalex.org/works"
params = {
    "search": "dream meaning",      # Keywords for your query
    "per_page": 100,                # Number of results per page
    "filter": "open_access.is_oa:true"  # Only fetch works that are open access
}

cursor = "*"
processed_count = 0         # Counter for works with available PDFs processed
desired_count = 10          # Set your desired number of works to process

# Define headers to mimic a browser request
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/90.0.4430.93 Safari/537.36"
    )
}

while processed_count < desired_count:
    params["cursor"] = cursor
    response = requests.get(base_url, params=params)
    
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code}")
        break

    data = response.json()
    works = data.get("results", [])
    if not works:
        break

    for work in works:
        work_id_full = work.get("id", "unknown")
        work_id = work_id_full.split("/")[-1]
        title = work.get("display_name", "No Title")
        
        # Check for a PDF URL in the primary location
        primary_location = work.get("primary_location") or {}
        pdf_url = primary_location.get("pdf_url")
        
        if not pdf_url:
            continue  # Skip this work if no PDF is provided
        
        try:
            # Download the PDF into memory (without saving to disk)
            pdf_response = requests.get(pdf_url, headers=headers)
            if pdf_response.status_code != 200:
                continue
        except Exception as e:
            continue
        
        try:
            # Extract text from the PDF using a BytesIO buffer
            pdf_data = BytesIO(pdf_response.content)
            reader = PyPDF2.PdfReader(pdf_data)
            extracted_text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text += page_text
        except Exception as e:
            continue
        
        # Create a JSON-friendly dictionary with metadata and extracted text
        work_data = {
            "id": work.get("id"),
            "title": title,
            "pdf_url": pdf_url,
            "pdf_text": extracted_text
        }
        pdf_texts.append(work_data)
        processed_count += 1
        print(f"Processed {processed_count} works with open-access PDFs")
        if processed_count >= desired_count:
            break

    # Update the cursor for pagination from the API's metadata
    meta = data.get("meta", {})
    next_cursor = meta.get("next_cursor")
    if not next_cursor or next_cursor == cursor:
        break
    cursor = next_cursor
    time.sleep(1)  # Politeness delay between API requests

# Save the extracted PDF texts and metadata to a JSON file
output_filename = "pdf_texts.json"
with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(pdf_texts, f, indent=4, ensure_ascii=False)

print(f"Saved PDF text data for {len(pdf_texts)} works to '{output_filename}'.")
