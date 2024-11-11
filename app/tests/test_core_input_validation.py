import pytest

from app.core.inout_validation import validate_currency


@pytest.mark.asyncio
async def test_validate_currency_invalid():
    @validate_currency
    async def my_function(currency: str):
        return currency

    result = await my_function(currency="mickey_mouse")
    assert result is None


@pytest.mark.asyncio
async def test_validate_currency_valid():
    @validate_currency
    async def my_function(currency: str):
        return currency

    result = await my_function(currency="EUR")
    assert result is not None
