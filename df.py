import requests
import os
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()
API_KEY = os.getenv("CMC_API_KEY")

BASE_URL = "https://pro-api.coinmarketcap.com/v1"
HEADERS = {
    "X-CMC_PRO_API_KEY": API_KEY,
    "Accept": "application/json"
}

@lru_cache(maxsize=1000)
def get_crypto(start: int = 1, convert: str = "USD") -> list | None:
    endpoint = f"{BASE_URL}/cryptocurrency/listings/latest"
    params = {
        "start": str(start),
        "limit": "1000",
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

def print_crypto(cryptos: list, page_size: int, page: int):
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_data = cryptos[start_idx:end_idx]

    print(f"{'№':<4} {'ID':<7} {'Название':<12} {'Символ':<6} {'Цена ($)':>12} {'Капитализация':>15}")
    print("-" * 65)
    for idx, coin in enumerate(page_data, start=start_idx + 1):
        quote = coin["quote"]["USD"]
        print(f"{idx:<4} {coin['id']:<7} {coin['name']:<12} {coin['symbol']:<6} "
              f"${quote['price']:>10.2f} ${quote['market_cap']:>14,.0f}")

def find_crypto(cryptos: list, name: str) -> list:
    return [coin for coin in cryptos if name.lower() in coin['name'].lower()]

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
              
if __name__ == "__main__":
    current_start = 1
    current_page = 1
    page_size = 10

    cryptos = get_crypto()
    if not cryptos:
            print("Data fetching error")
    while(True):
        print_crypto(cryptos=cryptos, page_size=page_size, page=current_page)

        print(f"Страница позиций {current_start}-{page_size * current_page}")
        print("Нажмите Enter для следующей страницы, q для выхода")

        user_input = input("> ").strip().lower()
        if user_input == 'q':
            break
        elif user_input == 'n' or user_input == '':
            current_start += page_size
            current_page += 1
        elif user_input == 'p' and current_page > 1:
            current_start -= page_size
            current_page -= 1
        elif user_input == 'f':
            print("Введите название криптовалюты для поиска:")
            search_name = input("> ").strip()
            results = find_crypto(cryptos, search_name)
            if results:
                clear_screen()
                print(f"Результаты поиска для '{search_name}':")
                print_crypto(results, page_size=len(results), page=1)
                print("Нажмите любую клавишу для продолжения")
                input()
            else:
                print("Криптовалюта не найдена.\nНажмите любую клавишу для продолжения")
                input()
        else: print("Неверная комнада")
        clear_screen()
