import pytest
import httpx
import respx
from src.services.btmc_service import BTMCService

# --- Dữ liệu giả lập (Mock Data) ---
MOCK_XML_FULL = """
<DataList>
    <Data row="1" n_1="BẠC MIẾNG PHÚ QUÝ Ag 999 1 KG 1000 GRAM (PHÚ QUÝ)" pb_1="80533132" ps_1="83013126" />
    <Data row="102" n_102="VÀNG MIẾNG VRTL (Vàng Rồng Thăng Long)" pb_102="17800000" ps_102="18100000" />
</DataList>
"""

MOCK_XML_SINGLE_ITEM = """
<DataList>
    <Data row="1" n_1="BẠC MIẾNG" pb_1="80000000" ps_1="82000000" />
</DataList>
"""

MOCK_XML_INVALID_STRUCTURE = "<Invalid>No Data Here</Invalid>"


@pytest.fixture
def btmc():
    return BTMCService(api_key="test_api_key")


@pytest.mark.asyncio
@respx.mock
async def test_fetch_success(btmc):
    """Trường hợp 1: API trả về XML đầy đủ và đúng định dạng."""
    respx.get(btmc.url).mock(return_value=httpx.Response(200, text=MOCK_XML_FULL))

    results = await btmc.fetch_btmc_price()

    assert results is not None
    assert len(results) == 2
    assert "VÀNG MIẾNG VRTL (Vàng Rồng Thăng Long)" in results
    assert results["VÀNG MIẾNG VRTL (Vàng Rồng Thăng Long)"]["buy"] == "17,800,000"


@pytest.mark.asyncio
@respx.mock
async def test_fetch_partial_data(btmc):
    """Trường hợp 2: API trả về thiếu một số mặt hàng chúng ta cần."""
    respx.get(btmc.url).mock(
        return_value=httpx.Response(200, text=MOCK_XML_SINGLE_ITEM)
    )

    results = await btmc.fetch_btmc_price()

    assert "BẠC MIẾNG PHÚ QUÝ Ag 999 1 KG 1000 GRAM (PHÚ QUÝ)" in results
    assert "VÀNG MIẾNG VRTL (Vàng Rồng Thăng Long)" not in results


@pytest.mark.asyncio
@respx.mock
async def test_fetch_http_error(btmc):
    """Trường hợp 3: Lỗi kết nối (404, 500, timeout)."""
    respx.get(btmc.url).mock(return_value=httpx.Response(500))

    results = await btmc.fetch_btmc_price()
    assert results is None


@pytest.mark.asyncio
@respx.mock
async def test_fetch_invalid_xml(btmc):
    """Trường hợp 4: API trả về nội dung không phải XML hoặc cấu trúc lạ."""
    respx.get(btmc.url).mock(
        return_value=httpx.Response(200, text=MOCK_XML_INVALID_STRUCTURE)
    )

    results = await btmc.fetch_btmc_price()
    assert results == {}


@pytest.mark.asyncio
async def test_parse_invalid_price_format(btmc):
    """Trường hợp 5: Giá trị giá (buy/sell) không phải là số."""
    bad_item = {"@row": "102", "@pb_102": "KHÔNG_CÓ_GIÁ", "@ps_102": "18100000"}

    result = await btmc.get_price_from_data(bad_item, "102")
    assert result is None


@pytest.mark.asyncio
async def test_parse_missing_price_keys(btmc):
    """Trường hợp 6: Thiếu hẳn key giá trong dictionary."""
    bad_item = {"@row": "102"}  # Thiếu @pb_102 và @ps_102

    result = await btmc.get_price_from_data(bad_item, "102")
    assert result is None
