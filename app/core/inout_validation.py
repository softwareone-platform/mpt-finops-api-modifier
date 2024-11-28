import functools
import logging

from currency_codes.exceptions import CurrencyNotFoundError
from currency_codes.main import get_currency_by_code

logger = logging.getLogger(__name__)
DEFAULT_CURRENCY = "USD"


def validate_currency(func):
    """
    Validates the currency code

    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        currency = kwargs.get("currency", DEFAULT_CURRENCY)
        try:
            get_currency_by_code(currency)
        except CurrencyNotFoundError:
            logger.error(f"Invalid currency: {currency}.")
            # replace None with a custom exception
            return None
        return await func(*args, **kwargs)

    return wrapper
