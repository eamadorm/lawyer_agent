import datetime
import sys
import time
from typing import List, Dict, Optional
import urllib3

import requests
from bs4 import BeautifulSoup

# Disable SSL warnings when importing the module
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL_HOST = "https://www.dof.gob.mx"
BASE_URL = "https://www.dof.gob.mx/index.php"

def get_dof_news_by_date(date_obj: datetime.date) -> List[Dict]:
    """
    Gets news for a specific date from the DOF website.

    Args:
        date_obj (datetime.date): The date to scrape news for.

    Returns:
        List[Dict]: A list of dictionaries containing news details.
    """
    try:
        params = {
            'year': date_obj.year,
            'month': date_obj.month,
            'day': date_obj.day
        }
        
        # 30-second timeout for robustness
        response = requests.get(BASE_URL, params=params, verify=False, timeout=30)
        response.raise_for_status()
        
        if "No hay datos para la fecha seleccionada" in response.text:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        news_list = []
        current_section = "No Section"
        date_str = date_obj.strftime("%d/%m/%Y")
        
        # Find subtitles (sections) and links (news) in order
        elements = soup.find_all(['td', 'a'], class_=['subtitle_azul', 'enlaces'])
        
        for el in elements:
            if el.name == 'td' and 'subtitle_azul' in el.get('class', []):
                current_section = el.get_text(strip=True)
            
            elif el.name == 'a' and 'enlaces' in el.get('class', []):
                text = el.get_text(strip=True)
                
                # Basic cleaning filters
                if len(text) < 5 or "búsqueda avanzada" in text.lower():
                    continue
                    
                href = el.get('href', '')
                if href and not href.startswith('http'):
                    link_final = f"{BASE_URL_HOST}/{href}" if href.startswith('nota_detalle') else f"{BASE_URL_HOST}{href}"
                else:
                    link_final = href

                item = {
                    'Fecha': date_str,
                    'Sección': current_section,
                    'Título': text,
                    'Link': link_final
                }
                news_list.append(item)
            
        return news_list
    
    except Exception as e:
        print(f"Error fetching DOF for {date_obj}: {e}", file=sys.stderr)
        return []

def scrape_dof(start_date_str: Optional[str] = None, end_date_str: Optional[str] = None) -> List[Dict]:
    """
    Executes the pipeline for a date range.
    If start_date is None, uses today. Accepted formats: 'DD/MM/YYYY' or 'YYYY-MM-DD'.

    Args:
        start_date_str (Optional[str]): Start date string. Defaults to None.
        end_date_str (Optional[str]): End date string. Defaults to None.

    Returns:
        List[Dict]: A list of all scraped news items.
    """
    # Date normalization
    now = datetime.datetime.now().date()
    
    if not start_date_str:
        start_date = now
        end_date = now
    else:
        start_date = parse_date(start_date_str)
        if end_date_str:
            end_date = parse_date(end_date_str)
        else:
            end_date = start_date
            
    if start_date > end_date:
        raise ValueError("Start date is after end date.")

    all_news = []
    current_date = start_date
    delta = datetime.timedelta(days=1)
    
    while current_date <= end_date:
        news_day = get_dof_news_by_date(current_date)
        all_news.extend(news_day)
        current_date += delta
        # Small throttle to avoid blocks
        time.sleep(0.5)
        
    return all_news

def parse_date(date_str: str) -> datetime.date:
    """
    Helper to parse dates in common formats.

    Args:
        date_str (str): The date string to parse.

    Returns:
        datetime.date: The parsed date object.
    """
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Date format not recognized: {date_str}")
