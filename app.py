import requests
import os
from dotenv import load_dotenv
from functools import lru_cache
import flet as ft

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
    params = {"start": str(start), "limit": "1000", "convert": convert}
    try:
        response = requests.get(endpoint, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        if data and data.get("status", {}).get("error_code") == 0:
            return data["data"]
        print(f"API ERROR: {data.get('status', {}).get('error_message', 'Unknown')}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"NET ERROR: {e}")
        return None

def find_crypto(cryptos: list, name: str) -> list:
    if not name: return cryptos
    return [c for c in cryptos if name.lower() in c["name"].lower()]

def format_num(v): return f"{v:,.0f}" if v is not None else "N/A"
def format_price(v): return f"${v:,.2f}" if v is not None else "N/A"

def main(page: ft.Page):
    page.title = "Crypto Tracker 💰"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = "auto"
    
    cryptos = []
    filtered_cryptos = []
    current_page = 1
    page_size = 15
    
    status_text = ft.Text("Загрузка данных...", color="orange")
    search_field = ft.TextField(
        label="🔍 Поиск по названию",
        width=400,
        on_change=lambda e: apply_search(),
        border_radius=10,
        prefix_icon="search"
    )
    
    crypto_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("№", weight="bold")),
            ft.DataColumn(ft.Text("Название", weight="bold")),
            ft.DataColumn(ft.Text("Символ", weight="bold")),
            ft.DataColumn(ft.Text("Цена", weight="bold"), numeric=True),
            ft.DataColumn(ft.Text("Капитализация", weight="bold"), numeric=True),
            ft.DataColumn(ft.Text("В обращении", weight="bold"), numeric=True),
        ],
        rows=[],
        column_spacing=15,
        expand=True,
    )
    
    pagination_text = ft.Text("", size=12, color="grey400")
    
    def update_table():
        nonlocal current_page
        start_idx = (current_page - 1) * page_size
        end_idx = start_idx + page_size
        page_data = filtered_cryptos[start_idx:end_idx]
        
        crypto_table.rows.clear()
        for i, coin in enumerate(page_data, start=start_idx + 1):
            q = coin["quote"]["USD"]
            crypto_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(i))),
                    ft.DataCell(ft.Text(coin["name"], weight="w500")),
                    ft.DataCell(ft.Text(coin["symbol"], weight="bold", color="blue300")),
                    ft.DataCell(ft.Text(format_price(q.get("price")))),
                    ft.DataCell(ft.Text(format_num(q.get("market_cap")))),
                    ft.DataCell(ft.Text(format_num(coin.get("circulating_supply")))),
                ])
            )
        
        total = max(1, (len(filtered_cryptos) + page_size - 1) // page_size)
        pagination_text.value = f"Страница {current_page} из {total} | Всего: {len(filtered_cryptos)}"
        btn_prev.disabled = current_page == 1
        btn_next.disabled = current_page >= total or total == 0
        page.update()
    
    def apply_search():
        nonlocal current_page
        q = search_field.value.strip()
        filtered_cryptos.clear()
        filtered_cryptos.extend(find_crypto(cryptos, q))
        current_page = 1
        update_table()
    
    def go_prev(e):
        nonlocal current_page
        if current_page > 1:
            current_page -= 1
            update_table()
    
    def go_next(e):
        nonlocal current_page
        total = max(1, (len(filtered_cryptos) + page_size - 1) // page_size)
        if current_page < total:
            current_page += 1
            update_table()
    
    def refresh_data(e):
        nonlocal cryptos, filtered_cryptos, current_page
        status_text.value = "🔄 Обновление..."
        status_text.color = "orange"
        page.update()
        
        get_crypto.cache_clear()
        data = get_crypto()
        
        if data:
            cryptos = data.copy()
            filtered_cryptos = cryptos.copy()
            current_page = 1
            status_text.value = f"✓ Загружено {len(cryptos)} криптовалют"
            status_text.color = "green"
            apply_search()
        else:
            status_text.value = "❌ Ошибка загрузки"
            status_text.color = "red"
            page.update()
    
    btn_prev = ft.ElevatedButton("⬅️ Назад", on_click=go_prev, disabled=True)
    btn_next = ft.ElevatedButton("Вперёд ➡️", on_click=go_next, disabled=True)
    btn_refresh = ft.ElevatedButton("🔄 Обновить данные", on_click=refresh_data)
    
    page.add(
        ft.Column([
            ft.Row([
                ft.Text("💰 Crypto Tracker", size=24, weight="bold"),
                btn_refresh
            ], alignment=ft.MainAxisAlignment.CENTER),
            status_text,
            ft.Divider(height=20, color="transparent"),
            search_field,
            ft.Container(
                content=crypto_table,
                border_radius=10,
                padding=10,
                bgcolor="surface_variant",
                expand=True
            ),
            ft.Divider(height=10, color="transparent"),
            ft.Row([btn_prev, pagination_text, btn_next], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
    )
    
    refresh_data(None)

if __name__ == "__main__":
    ft.app(main=main)