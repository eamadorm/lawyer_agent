import functions_framework
from flask import Request
import sys
import datetime
from loguru import logger
from .config import settings
from .scraper import scrape_dof
from .bq_utils import insert_rows_from_json

# Logging configuration
logger.remove()
logger.add(sys.stderr, level="DEBUG")

@functions_framework.http
def scrape_dof_function(request: Request):
    """
    Cloud Function to scrape DOF news and insert into BigQuery.
    Triggered via HTTP.

    Args:
        request (flask.Request): The HTTP request object.

    Returns:
        tuple: A JSON response and HTTP status code.
    """
    # Get parameters from query string or JSON body
    request_json = request.get_json(silent=True)
    request_args = request.args

    start_date = None
    end_date = None

    if request_args and 'start_date' in request_args:
        start_date = request_args['start_date']
    elif request_json and 'start_date' in request_json:
        start_date = request_json['start_date']

    if request_args and 'end_date' in request_args:
        end_date = request_args['end_date']
    elif request_json and 'end_date' in request_json:
        end_date = request_json['end_date']

    # Simple health check if no parameters and method is GET
    if request.method == 'GET' and not start_date and not end_date and request.path == '/health':
         return {"status": "ok", "service": "dof-scraper-function"}, 200

    try:
        # 1. Scraping
        logger.info(f"Starting scraping: start={start_date}, end={end_date}")
        raw_data = scrape_dof(start_date, end_date)
        
        if not raw_data:
            return {
                "message": "No news found for the selected range.",
                "count": 0,
                "data": []
            }, 200

        # 2. Data transformation for BigQuery
        bq_rows = []
        for item in raw_data:
            bq_rows.append({
                "published_date": parse_date_for_bq(item["Fecha"]),
                "section": item["Sección"],
                "title": item["Título"],
                "link": item["Link"]
            })
            
        # 3. BigQuery Insertion
        logger.info(f"Inserting {len(bq_rows)} rows into {settings.DATASET_NAME}.{settings.TABLE_NAME}")
        logger.debug(f"table_name = {settings.TABLE_NAME}")
        logger.debug(f"dataset_name = {settings.DATASET_NAME}")
        logger.debug(f"project_id = {settings.PROJECT_ID}")
        insert_rows_from_json(
            table_name=settings.TABLE_NAME,
            dataset_name=settings.DATASET_NAME,
            project_id=settings.PROJECT_ID,
            rows=bq_rows
        )
        
        return {
            "status": "success",
            "message": f"Inserted {len(bq_rows)} news items into BigQuery.",
            "count": len(bq_rows),
            "bq_target": f"{settings.PROJECT_ID}.{settings.DATASET_NAME}.{settings.TABLE_NAME}",
        }, 200

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return {"error": str(e)}, 400
    except Exception as e:
        logger.exception(f"Internal error: {e}")
        return {"error": f"Internal Server Error: {str(e)}"}, 500

def parse_date_for_bq(date_str: str) -> str:
    """
    Transforms DD/MM/YYYY to YYYY-MM-DD for BigQuery DATE type.

    Args:
        date_str (str): The input date string.

    Returns:
        str: The formatted date string or original if parsing fails.
    """
    try:
        dt = datetime.datetime.strptime(date_str, "%d/%m/%Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return date_str # Fallback if it comes in another format

if __name__ == "__main__":
    import argparse
    # Local execution for testing purposes (mocks the Cloud Function request)
    parser = argparse.ArgumentParser(description="Run DOF scraper locally.")
    parser.add_argument("--start_date", type=str, help="Start date in DD/MM/YYYY format")
    parser.add_argument("--end_date", type=str, help="End date in DD/MM/YYYY format")
    args = parser.parse_args()

    class MockRequest:
        def __init__(self, json_data=None, args=None):
            self._json = json_data
            self.args = args or {}
            self.method = "GET"
            self.path = "/" # Default path

        def get_json(self, silent=True):
            return self._json

    logger.info("Executing function locally...")
    
    # Construct arguments dictionary
    request_args = {}
    if args.start_date:
        request_args['start_date'] = args.start_date
    if args.end_date:
        request_args['end_date'] = args.end_date

    logger.info(f"Arguments: {request_args}")

    mock_req = MockRequest(args=request_args) 
    
    response = scrape_dof_function(mock_req)
    print("\n--- Execution Result ---")
    print(response)
