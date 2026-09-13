import json
from datetime import datetime

from bs4 import BeautifulSoup

from .client import SchoolTodayClient


class ClassWall:
    def __init__(self, client: SchoolTodayClient):
        self.client = client

    def get_page(self):
        url = "https://school-today.com/ClassWall"

        response = self.client.session.get(url)

        if response.status_code != 200:
            raise RuntimeError(
                f"Не удалось получить ClassWall: {response.status_code}"
            )

        return response.text

    def get_pages(self):
        first_page = self.get_page()

        soup = BeautifulSoup(first_page, "html.parser")

        load_more_button = soup.find(
            "a",
            class_="btnLoadMore"
        )

        if load_more_button is None:
            return [first_page]

        ticks = load_more_button.get("data-ticks")

        if not ticks:
            return [first_page]

        load_more_url = (
            "https://school-today.com/ClassWall/LoadMore"
            "?classID=13557"
            "&schoolYearId=1187"
            f"&lastTicks={ticks}"
        )

        response = self.client.session.get(load_more_url)

        if response.status_code != 200:
            raise RuntimeError(
                f"Не удалось получить ClassWall LoadMore: "
                f"{response.status_code}"
            )

        second_page = response.text

        return [first_page, second_page]

    def parse_posts(self, pages):
        posts = []

        current_year = datetime.now().year
        current_date = None

        for html in pages:
            soup = BeautifulSoup(html, "html.parser")

            timeline = soup.find("ul", class_="timeline")

            if timeline is None:
                continue

            for element in timeline.find_all("li", recursive=False):

                if "timeline-separator" in element.get("class", []):
                    datetime_value = element.get("data-datetime")

                    if datetime_value:
                        current_date = datetime.strptime(
                            f"{datetime_value}.{current_year}",
                            "%d.%m.%Y"
                        ).date()

                    continue

                if "timeline-end" in element.get("class", []):
                    continue

                text_element = element.find(
                    "p",
                    style="white-space: pre-line"
                )

                description = ""

                if text_element:
                    description = text_element.get_text(
                        " ",
                        strip=True
                    )

                author = ""

                text = element.get_text(
                    " ",
                    strip=True
                )

                if text.startswith("СК "):
                    parts = text.split(" ", 3)

                    if len(parts) >= 3:
                        author = f"{parts[1]} {parts[2]}"

                files = []

                for media in element.find_all(
                    attrs={"data-object": True}
                ):
                    data_object = media.get("data-object")

                    try:
                        media_data = json.loads(data_object)
                    except (json.JSONDecodeError, TypeError):
                        continue

                    file_type = media_data.get("FileType")

                    if file_type == 1:
                        media_type = "photo"
                    elif file_type == 2:
                        media_type = "video"
                    else:
                        media_type = "unknown"

                    files.append({
                        "id": media_data.get("ID"),
                        "name": media_data.get("Name"),
                        "url": media_data.get("StorageURL"),
                        "preview_url": media_data.get(
                            "PreviewStorageURL"
                        ),
                        "type": media_type,
                        "content_type": media_data.get(
                            "ContentType"
                        ),
                    })

                posts.append({
                    "date": current_date.isoformat()
                    if current_date else None,
                    "description": description,
                    "author": author,
                    "files": files,
                })

        return posts

    def group_posts_by_date(self, posts):
        grouped = {}

        for post in posts:
            date = post["date"]

            if date not in grouped:
                grouped[date] = []

            grouped[date].append(post)

        return grouped