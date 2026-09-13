import os

from dotenv import load_dotenv


load_dotenv()


class Config:
    def __init__(self):
        self.email = os.getenv("SCHOOL_EMAIL")
        self.password = os.getenv("SCHOOL_PASSWORD")

        self.classwall_archive_dir = os.getenv(
            "CLASSWALL_ARCHIVE_DIR",
            "school_today_media"
        )

        self.classwall_class_id = os.getenv(
            "CLASSWALL_CLASS_ID"
        )

        self.classwall_school_year_id = os.getenv(
            "CLASSWALL_SCHOOL_YEAR_ID"
        )