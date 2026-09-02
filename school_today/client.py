import requests

from bs4 import BeautifulSoup

from .config import Config


class SchoolTodayClient:

    def __init__(self):
        self.session = requests.Session()

        config = Config()

        self.email = config.email
        self.password = config.password

    def login(self):
        login_url = "https://school-today.com/Account/Login"

        response = self.session.get(login_url)

        print("Страница входа:", response.status_code)

        soup = BeautifulSoup(response.text, "html.parser")

        token = soup.find(
            "input",
            {"name": "__RequestVerificationToken"}
        )

        if token is None:
            print("Токен не найден!")
            return False

        token = token.get("value")

        data = {
            "Step": "Login",
            "Verification": "",
            "Email": self.email,
            "Password": self.password,
            "RememberMe": "true",
            "__RequestVerificationToken": token,
        }

        response = self.session.post(
            login_url,
            data=data,
            allow_redirects=True
        )

        print("После входа:", response.status_code)
        print("URL:", response.url)

        return response.url == "https://school-today.com/Profile"