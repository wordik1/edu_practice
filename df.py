import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("CMC_API_KEY")

BASE_URL = "https://pro-api.coinmarketcap.com/v1"
HEADERS = {
    "X-CMC_PRO_API_KEY": API_KEY,
    "Accept": "application/json"
}

def get_crypto(limit: int = 5, convert: str = "USD") -> list | None:
    endpoint = f"{BASE_URL}/cryptocurrency/listings/latest"
    params = {
        "start": "1",
        "limit": str(limit),
        "convert": convert
    }

    try:
        response = requests.get(endpoint, headers=HEADERS, params=params)
        response.raise_for_status()

        data = response.json()
        if(data.get("status", {}).get("error_code") != 0):
            print(f"API ERROR: {data['status'].get('error_message')}")
            return None
        return data["data"]

    except requests.exceptions.RequestException as e:
        print(f"NET ERROR: {e}")
        return None

if __name__ == "__main__":
    cryptos = get_crypto(limit = 5, convert="USD")
    if cryptos:
        print(f"{'Название':<15} {'Символ':<6} {'Цена':>12} {'Капитализация':>15}")
        print("-" * 52)
        for coin in cryptos:
            quote = coin["quote"]["USD"]
            print(f"{coin['name']:<15} {coin['symbol']:<6} ${quote['price']:>11.2f} ${quote['market_cap']:>14,.0f}")
