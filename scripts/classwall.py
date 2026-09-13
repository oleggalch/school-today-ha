import json
from datetime import datetime
from pathlib import Path

from school_today.client import SchoolTodayClient
from school_today.classwall import ClassWall
from school_today.config import Config


def make_filename(file_data):
    file_id = file_data.get("id")
    original_name = file_data.get("name") or ""

    if not file_id:
        raise RuntimeError("У файла отсутствует ID")

    if file_data.get("type") == "video":
        if original_name.lower().startswith("video."):
            return f"Video_{file_id}"

    if original_name:
        return original_name

    return file_id


def download_file(client, file_data, destination):
    url = file_data.get("url")

    if not url:
        raise RuntimeError(
            f"У файла нет URL: {file_data.get('id')}"
        )

    response = client.session.get(
        url,
        stream=True
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Ошибка скачивания {response.status_code}: {url}"
        )

    with destination.open("wb") as file:
        for chunk in response.iter_content(
            chunk_size=1024 * 1024
        ):
            if chunk:
                file.write(chunk)


def load_existing_ids(archive_dir):
    existing = {}

    for metadata_file in archive_dir.glob(
        "*/*/*/metadata.json"
    ):
        try:
            with metadata_file.open(
                "r",
                encoding="utf-8"
            ) as file:
                metadata = json.load(file)
        except Exception:
            continue

        for post in metadata.get("posts", []):
            for media in post.get("files", []):
                file_id = media.get("id")
                filename = media.get("filename")

                if file_id and filename:
                    existing[file_id] = filename

    return existing


def save_day(
    day_dir,
    date,
    posts,
    client,
    existing_ids
):
    day_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    metadata_posts = []

    for post in posts:
        metadata_files = []

        for media in post["files"]:
            file_id = media.get("id")

            if not file_id:
                continue

            filename = existing_ids.get(file_id)

            if not filename:
                filename = make_filename(media)
                existing_ids[file_id] = filename

            file_path = day_dir / filename

            if not file_path.exists():
                download_file(
                    client,
                    media,
                    file_path
                )

            metadata_file = dict(media)
            metadata_file["filename"] = filename

            metadata_files.append(
                metadata_file
            )

        metadata_posts.append({
            "date": post["date"],
            "description": post["description"],
            "author": post["author"],
            "files": metadata_files,
        })

    metadata = {
        "date": date,
        "posts": metadata_posts,
    }

    metadata_path = day_dir / "metadata.json"

    with metadata_path.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            metadata,
            file,
            ensure_ascii=False,
            indent=2
        )


def main():
    config = Config()

    archive_dir = Path(
        config.classwall_archive_dir
    )

    client = SchoolTodayClient()

    if not client.login():
        raise RuntimeError(
            "Не удалось войти в School Today"
        )

    classwall = ClassWall(client)

    pages = classwall.get_pages()
    posts = classwall.parse_posts(pages)

    grouped = classwall.group_posts_by_date(
        posts
    )

    existing_ids = load_existing_ids(
        archive_dir
    )

    for date, day_posts in grouped.items():
        if not date:
            continue

        date_object = datetime.strptime(
            date,
            "%Y-%m-%d"
        ).date()

        day_dir = (
            archive_dir
            / f"{date_object.year:04d}"
            / f"{date_object.month:02d}"
            / f"{date_object.day:02d}"
        )

        save_day(
            day_dir,
            date,
            day_posts,
            client,
            existing_ids
        )


if __name__ == "__main__":
    main()