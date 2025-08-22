import httpx
from httpx_retries import Retry, RetryTransport


def http_client_factory(
    retry_total: int = 5, retry_backoff_factor: float = 0.5
) -> httpx.AsyncClient:
    """Create an HTTPX AsyncClient.

    Args:
        retry_total: The number of times to retry when a request failure
            occurs.
        retry_backoff_factor: Backoff factor to determine length of time
            between retry attempts.
    """
    return httpx.AsyncClient(
        transport=RetryTransport(retry=Retry(total=5, backoff_factor=0.5))
    )
