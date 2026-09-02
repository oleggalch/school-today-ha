from datetime import datetime, timedelta

from bs4 import BeautifulSoup


class Menu:

    MONTHS = {
        "січня": 1,
        "лютого": 2,
        "березня": 3,
        "квітня": 4,
        "травня": 5,
        "червня": 6,
        "липня": 7,
        "серпня": 8,
        "вересня": 9,
        "жовтня": 10,
        "листопада": 11,
        "грудня": 12,
    }

    def __init__(self, client):
        self.client = client
        self.days = []

    def get_menu(self, date_from, date_to=None):
        if date_to is None:
            date_to = date_from

        if date_to < date_from:
            raise ValueError(
                "Конечная дата не может быть раньше начальной."
            )

        result = []

        current_week = date_from - timedelta(
            days=date_from.weekday()
        )

        last_week = date_to - timedelta(
            days=date_to.weekday()
        )

        while current_week <= last_week:

            days = self.get_week(current_week)

            for day in days:
                if date_from <= day["date"] <= date_to:
                    result.append(day)

            current_week += timedelta(days=7)

        self.days = result

        return result

    def get_menu_today(self):
        today = datetime.now().date()

        return self.get_menu(today)

    def get_week(self, week_start):
        menu_url = (
            "https://school-today.com/"
            "MenuPupilOverview/MenuView"
        )

        params = {
            "weekDay": week_start.strftime("%m.%d.%Y")
        }

        response = self.client.session.get(
            menu_url,
            params=params
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Не удалось получить меню. "
                f"Код: {response.status_code}"
            )

        return self.parse_days(response.text)

    def parse_days(self, html):
        soup = BeautifulSoup(html, "html.parser")

        days = soup.find_all("h4")

        result = []

        for day in days:
            day_name = day.get_text(" ", strip=True)

            day_text = day_name.split(", ", 1)[1]

            parts = day_text.split(" ", 1)

            day_number = int(parts[0])
            month_name = parts[1]

            month = self.MONTHS[month_name]

            year = datetime.now().year

            day_date = datetime(
                year,
                month,
                day_number
            ).date()

            day_data = {
                "date": day_date,
                "day": day_name,
                "meals": []
            }

            element = day.parent

            while element:
                element = element.find_next_sibling()

                if element is None:
                    break

                if element.find("h4"):
                    break

                if element.name != "table":
                    continue

                meal = element.find(
                    "div",
                    class_="fw-bold"
                )

                if meal is None:
                    continue

                meal_name = meal.get_text(
                    " ",
                    strip=True
                )

                meal_data = {
                    "name": meal_name,
                    "dishes": []
                }

                rows = element.find_all(
                    "tr",
                    class_="row"
                )

                for row in rows:
                    cells = row.find_all(
                        "td",
                        recursive=False
                    )

                    if len(cells) < 2:
                        continue

                    category = cells[0].get_text(
                        " ",
                        strip=True
                    )

                    if category == meal_name:
                        continue

                    dishes_cell = cells[1]

                    items = dishes_cell.find_all(
                        "div",
                        class_="row-meal"
                    )

                    for item in items:
                        text = item.get_text(
                            " ",
                            strip=True
                        )

                        if not text:
                            continue

                        dish_data = {
                            "category": category,
                            "name": text
                        }

                        meal_data["dishes"].append(
                            dish_data
                        )

                day_data["meals"].append(
                    meal_data
                )

            result.append(day_data)

        return result