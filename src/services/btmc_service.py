import httpx
import logging
import xmltodict
from typing import Dict, Optional


class BTMCService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "http://api.btmc.vn/api/BTMCAPI/getpricebtmc"
        self.fetch_items = {
            "1": "BẠC MIẾNG PHÚ QUÝ Ag 999 1 KG 1000 GRAM (PHÚ QUÝ)",
            "102": "VÀNG MIẾNG VRTL (Vàng Rồng Thăng Long)",
        }

    async def fetch_btmc_price(self) -> Optional[Dict[str, dict]]:
        """Main entry point to get cleaned price data."""
        params = {"key": self.api_key}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.url, params=params)
                response.raise_for_status()
                return await self._process_xml(response.text)
        except (httpx.HTTPError, Exception) as e:
            logging.error(f"Network error fetching BTMC price: {e}")
            return None

    async def _process_xml(self, xml_content: str) -> Dict[str, dict]:
        """Internal logic to parse XML and filter items."""
        results = {}
        try:
            data_dict = xmltodict.parse(xml_content)
            # Handle cases where Data might be a single dict or a list
            raw_data = data_dict.get("DataList", {}).get("Data", [])
            if isinstance(raw_data, dict):
                raw_data = [raw_data]

            data_items = {item.get("@row"): item for item in raw_data}

            for row_id, label in self.fetch_items.items():
                if row_id not in data_items:
                    logging.warning(f"Item {row_id} not found in BTMC feed.")
                    continue

                price_data = await self.get_price_from_data(data_items[row_id], row_id)
                if price_data:
                    results[label] = price_data

            return results
        except Exception as e:
            logging.error(f"XML Parsing error: {e}")
            return {}

    async def get_price_from_data(self, item: dict, key: str) -> Optional[dict]:
        """Extract and format buy/sell prices."""
        try:
            price_buy_str = item.get(f"@pb_{key}")
            price_sell_str = item.get(f"@ps_{key}")

            if not price_buy_str or not price_sell_str:
                return None

            return {
                "buy": f"{float(price_buy_str):,.0f}",
                "sell": f"{float(price_sell_str):,.0f}",
            }
        except (ValueError, TypeError) as e:
            logging.error(f"Error parsing price for key {key}: {e}")
            return None
