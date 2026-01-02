import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
import sys
from datetime import datetime
import unicodedata
import concurrent.futures
from loguru import logger
from .config import settings
from .gcs_utils import upload_bytes, bucket_exists

# Regex Patterns
NAME_DATE_PATTERN = re.compile(r"^(.*?)(DOF\s+\d{2}/\d{2}/\d{4})", re.IGNORECASE)
DATE_PATTERN = re.compile(r"(\d{2}/\d{2}/\d{4})")

def remove_accents(input_str):
    if not input_str: return ""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def clean_filename(text):
    if not text: return "unknown"
    # 1. Normalize and remove accents
    text = remove_accents(text)
    # 2. Replace newlines and tabs
    text = text.replace("\n", "_").replace("\r", "_").replace("\t", "_")
    
    # 3. Specific replacement: Parentheses and Quotes -> Underscore
    for char in ['(', ')', '"', "'"]:
        text = text.replace(char, "_")

    # 4. Remove non-alphanumeric characters (except _ and -)
    # Hyphen must be at the end or escaped
    text = re.sub(r'[^a-zA-Z0-9\s_-]', '', text)
    
    # 5. Collapse spaces and underscores
    text = re.sub(r'[\s_]+', '_', text.strip())
    
    # 6. Limit length
    return text[:100]

def format_date_iso(date_str):
    if not date_str: return None
    try:
        dt = datetime.strptime(date_str, "%d/%m/%Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return None

def process_law(row):
    """
    Downloads and uploads a single law PDF to GCS.
    Using global constants for simplicity in this script context.
    """
    pdf_url = row['url_pdf']
    clean_name = row['cleaned_law_name']
    formatted_date = row['formatted_last_update_date']
    
    file_name = f"{clean_name}-{formatted_date}.pdf"
    file_name = file_name.replace("_-", "-").replace("-_", "-")
    blob_path = f"{settings.GCS_FOLDER}/{file_name}"
    
    try:
        # Create a session with retry logic
        session = requests.Session()
        retry = requests.adapters.Retry(
            total=5, 
            backoff_factor=1, 
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = requests.adapters.HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        # Download with the session
        pdf_response = session.get(pdf_url, timeout=120)  # Increased timeout
        pdf_response.raise_for_status()
        pdf_bytes = pdf_response.content
        
        # Upload
        upload_bytes(
            blob_name=blob_path,
            bucket_name=settings.BUCKET_NAME,
            content_type="application/pdf",
            bytes_data=pdf_bytes
        )
        return f"SUCCESS: {file_name}"
    except Exception as e:
        logger.error(f"Error processing {file_name}: {e}")
        return f"ERROR: {file_name} -> {str(e)}"

def run_pipeline():
    """
    Main execution function to scrape and upload laws.
    """
    logger.info(f"Connecting to GCS Bucket: {settings.BUCKET_NAME}")
    if not bucket_exists(settings.BUCKET_NAME):
        logger.error(f"Bucket {settings.BUCKET_NAME} does not exist or is inaccessible.")
        return {"status": "error", "message": "Bucket not found"}

    logger.info(f"Fetching content from {settings.URL}")
    response = requests.get(settings.URL, timeout=30)
    response.raise_for_status()
    response.encoding = 'iso-8859-1'
    
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table')
    main_table = None
    max_rows = 0

    for table in tables:
        rows = table.find_all('tr')
        if len(rows) > max_rows:
            if "Nueva" in table.get_text() or "Publicación" in table.get_text():
                max_rows = len(rows)
                main_table = table
    
    if not main_table:
        logger.error("Could not find the main table.")
        return {"status": "error", "message": "Main table not found"}

    logger.info(f"Table found with {max_rows} rows.")
    
    data = []
    rows = main_table.find_all('tr')

    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 3:
            continue
            
        pdf_url = ""
        pdf_link = row.find('a', href=lambda x: x and x.lower().endswith('.pdf'))
        if pdf_link:
            href = pdf_link['href']
            pdf_url = href if href.startswith('http') else settings.BASE_URL + href
        if not pdf_url:
            continue

        # Col 1 Processing
        raw_col1 = cols[1].get_text(strip=True)
        raw_col1 = " ".join(raw_col1.split())
        match = NAME_DATE_PATTERN.search(raw_col1)
        
        nombre_ley = ""
        first_publication_in = ""
        first_publication_date = ""

        if match:
            nombre_ley = match.group(1).strip().title()
            full_date_text = match.group(2).strip()
            parts = full_date_text.split()
            if len(parts) >= 2:
                first_publication_in = parts[0]
                first_publication_date = parts[-1]
            else:
                first_publication_in = full_date_text
        else:
            nombre_ley = raw_col1.title()
            
        # Col 2 Processing
        raw_reforma = cols[2].get_text(strip=True) if len(cols) > 2 else ""
        date_match = DATE_PATTERN.search(raw_reforma)
        
        last_update_date = date_match.group(1) if date_match else ""
        last_update_in = "DOF" if "DOF" in raw_reforma.upper() else raw_reforma.replace(last_update_date, "").strip()

        # Cleaning & Formatting
        cleaned_law_name = clean_filename(nombre_ley)
        formatted_first_date = format_date_iso(first_publication_date)
        formatted_last_date = format_date_iso(last_update_date)
        
        # Fallback Logic
        if not formatted_last_date or "Sin reforma" in raw_reforma:
            formatted_last_date = formatted_first_date
            if not formatted_last_date:
                 formatted_last_date = "unknown"

        data.append({
            "law_name": nombre_ley,
            "cleaned_law_name": cleaned_law_name,
            "formatted_last_update_date": formatted_last_date,
            "url_pdf": pdf_url
        })

    df = pd.DataFrame(data)
    logger.info(f"Extracted {len(df)} laws. Starting parallel download/upload.")

    results = []
    # Convert to list of dicts for processing
    rows_to_process = [row for _, row in df.iterrows()]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=settings.MAX_WORKERS) as executor:
        future_to_law = {executor.submit(process_law, row): row for row in rows_to_process}
        for future in concurrent.futures.as_completed(future_to_law):
            results.append(future.result())

    errors = [r for r in results if r.startswith("ERROR")]
    success_count = len(results) - len(errors)
    
    logger.info(f"Process finished. Success: {success_count}, Errors: {len(errors)}")
    
    return {
        "status": "success",
        "total": len(results),
        "success": success_count,
        "errors": len(errors),
        "error_details": errors[:10] # Return first 10 errors sample
    }
