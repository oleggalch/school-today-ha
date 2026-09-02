from datetime import date

from school_today.client import SchoolTodayClient
from school_today.menu import Menu


client = SchoolTodayClient()

if client.login():
    print("\nАвторизация успешна!")

    menu = Menu(client)

    print("\n--- Меню за период ---")

    date_from = date(2026, 9, 7)
    date_to = date(2026, 9, 11)

    days = menu.get_menu(
        date_from,
        date_to
    )

    print(
        "Получено дней:",
        len(days)
    )

    for day in days:
        print(
            f"\n{day['date']} "
            f"({day['day']}):"
        )

        for meal in day["meals"]:
            print(f"\n  {meal['name']}:")

            for dish in meal["dishes"]:
                print(
                    f"    {dish['category']}: "
                    f"{dish['name']}"
                )

    print("\n--- Меню на сегодня ---")

    today = menu.get_menu_today()

    print(
        "Получено дней:",
        len(today)
    )

    for day in today:
        print(
            f"\n{day['date']} "
            f"({day['day']}):"
        )

        for meal in day["meals"]:
            print(f"\n  {meal['name']}:")

            for dish in meal["dishes"]:
                print(
                    f"    {dish['category']}: "
                    f"{dish['name']}"
                )

else:
    print("Авторизация не удалась.")