import os
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("INCOME_TAX_USERNAME")
PASSWORD = os.getenv("INCOME_TAX_PASSWORD")
BASE_URL = os.getenv("INCOME_TAX_URL", "https://www.incometax.gov.in")
DOWNLOAD_PATH = os.getenv("DOWNLOAD_PATH", "./downloads")
