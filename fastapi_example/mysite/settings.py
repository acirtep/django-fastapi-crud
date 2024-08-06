import os

from starlette.templating import Jinja2Templates

DATABASE_URL = os.getenv("DATABASE_URL")

templates = Jinja2Templates(directory="mysite/templates")
