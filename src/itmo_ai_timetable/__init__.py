import os

from itmo_ai_timetable.settings import Settings

settings = Settings()
os.environ["TZ"] = settings.tz
