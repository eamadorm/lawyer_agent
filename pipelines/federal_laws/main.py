import functions_framework
from flask import Request
import sys
from loguru import logger
from .scraper import run_pipeline

# Logging configuration
logger.remove()
logger.add(sys.stderr, level="INFO")

@functions_framework.http
def federal_laws_scraper_function(request: Request):
    """
    Cloud Function to scrape Federal Laws and upload PDFs to GCS.
    Triggered via HTTP.

    Args:
        request (flask.Request): The HTTP request object.

    Returns:
        tuple: A JSON response and HTTP status code.
    """
    # Simple health check
    if request.method == 'GET' and request.path == '/health':
         return {"status": "ok", "service": "federal-laws-scraper"}, 200

    try:
        logger.info("Triggering Federal Laws Scraper Pipeline...")
        
        result = run_pipeline()
        
        if result.get("status") == "error":
             return result, 500
             
        return result, 200

    except Exception as e:
        logger.exception(f"Internal error: {e}")
        return {"error": f"Internal Server Error: {str(e)}"}, 500

if __name__ == "__main__":
    # Local Test
    logger.info("Running locally...")
    res = run_pipeline()
    print(res)
