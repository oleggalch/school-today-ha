from bs4 import BeautifulSoup

from school_today.client import SchoolTodayClient
from school_today.menu import Menu


client = SchoolTodayClient()

if client.login():
    print("\nАвторизация успешна!")

    menu = Menu(client)

    html = menu.get_menu("09.01.2026")

    soup = BeautifulSoup(html, "html.parser")

    print("\nЗаголовки:")

    for tag in soup.find_all(["h1", "h2", "h3", "h4"]):
        text = tag.get_text(" ", strip=True)

        if text:
            print(text)

else:
    print("Авторизация не удалась.")