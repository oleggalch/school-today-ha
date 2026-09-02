from datetime import datetime, timedelta

from flask import Flask, jsonify

from .client import SchoolTodayClient
from .menu import Menu


app = Flask(__name__)


client = SchoolTodayClient()
menu = Menu(client)


def serialize_days(days):
    result = []

    for day in days:
        day_data = {
            "date": day["date"].isoformat(),
            "day": day["day"],
            "meals": []
        }

        for meal in day["meals"]:
            meal_data = {
                "name": meal["name"],
                "dishes": []
            }

            for dish in meal["dishes"]:
                meal_data["dishes"].append({
                    "category": dish["category"],
                    "name": dish["name"]
                })

            day_data["meals"].append(meal_data)

        result.append(day_data)

    return result


@app.route("/menu")
def get_menu():
    if not client.login():
        return jsonify({
            "error": "Авторизация не удалась."
        }), 401

    today = datetime.now().date()

    week_start = today - timedelta(
        days=today.weekday()
    )

    week_end = week_start + timedelta(days=6)

    days = menu.get_menu(
        week_start,
        week_end
    )

    return jsonify(serialize_days(days))


@app.route("/menu/today")
def get_menu_today():
    if not client.login():
        return jsonify({
            "error": "Авторизация не удалась."
        }), 401

    days = menu.get_menu_today()

    return jsonify(serialize_days(days))


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )