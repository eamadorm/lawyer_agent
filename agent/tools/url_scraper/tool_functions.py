from pydantic_ai import RunContext
from loguru import logger
import requests
import urllib3
from markdownify import markdownify as md
from .schemas import UrlScraperInput, UrlScraperOutput

# Suppress only the single InsecureRequestWarning from urllib3 needed
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def scrape_and_convert_to_markdown(ctx: RunContext, input_data: UrlScraperInput) -> UrlScraperOutput:
    """
    Fetches the content of a given URL and converts it to Markdown.

    Args:
        ctx: The context of the agent run.
        input_data: The input data containing the URL to scrape.

    Returns:
        A UrlScraperOutput object containing the Markdown content and status.
    """
    url = input_data.url
    try:
        logger.info(f"Scraping URL: {url}")
        
        # Add a user-agent to avoid being blocked by some sites
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Verify=False to handle sites with bad certs (common in gov sites)
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        
        html_content = response.text
        markdown_content = md(html_content, heading_style="ATX", strip=['script', 'style'])
        
        # Truncate content if it's too long? 
        # For now, let's keep it whole, but maybe add a warning if it's huge in log.
        if len(markdown_content) > 20000:
             logger.warning(f"Scraped content is very large: {len(markdown_content)} characters.")

        logger.info("Successfully scraped and converted to Markdown.")
        return UrlScraperOutput(
            content=markdown_content,
            url=url,
            status="success"
        )

    except requests.exceptions.RequestException as e:
        error_msg = f"Error fetching URL: {str(e)}"
        logger.error(error_msg)
        return UrlScraperOutput(
            content="",
            url=url,
            status=f"error: {error_msg}"
        )
    except Exception as e:
        error_msg = f"Unexpected error scraping URL: {str(e)}"
        logger.error(error_msg)
        return UrlScraperOutput(
            content="",
            url=url,
            status=f"error: {error_msg}"
        )
