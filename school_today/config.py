import os

from dotenv import load_dotenv


load_dotenv()


class Config:

    def __init__(self):
        self.email = os.getenv("SCHOOL_EMAIL")
        self.password = os.getenv("SCHOOL_PASSWORD")