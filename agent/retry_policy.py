from pydantic_ai.retries import AsyncTenacityTransport, RetryConfig, wait_retry_after
from httpx import AsyncClient, HTTPStatusError
from tenacity import retry_if_exception_type, stop_after_attempt, wait_exponential

# Code adapted from: https://ai.pydantic.dev/retries/
def create_retrying_client():
    """
    Create a client with smart retry habdling for multiple error types
    """

    def should_retry_status(response):
        if response.status_code in [429, 502, 503, 504]:
            response.raise_for_status()

    transport = AsyncTenacityTransport(
        config=RetryConfig(
            # Retry on HTTP errors and connection issues
            retry = retry_if_exception_type((HTTPStatusError, ConnectionError)),
            # Smart waiting: respects Retry-After headers, falls back to exponential backoff
            wait = wait_retry_after(
                fallback_strategy=wait_exponential(multiplier=1, max=60),
                max_wait=300,
            ),
            #Stop after 10 attempts
            stop = stop_after_attempt(10),

            # Re-raise the last exception of all retries fail
            reraise = True,
        ),
        validate_response=should_retry_status,
    )

    return AsyncClient(transport=transport)
