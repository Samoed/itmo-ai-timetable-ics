import requests

from db.base import Course
from itmo_ai_timetable import Settings


class CourseInfoRepository:
    settings = Settings()

    @staticmethod
    def add_link(course: Course) -> None:
        group_name = ""
        course_name = course.name
        if course.name.startswith("Работа в удаленных командах"):
            course_name = "Работа в удаленных командах"
            # from Работа в удаленных командах (в 19) -> в 19
            group_name = course.name.split("(")[1].replace(")", "")
        result = requests.post(
            CourseInfoRepository.settings.course_info_url + "/api/v1/integrations/google_calendar_links",
            json={
                "course_run_name": "Осень 2024",
                "course": {
                    "name": course_name,
                    "groups": [
                        {
                            "name": group_name,
                            "link": f"https://calendar.google.com/calendar/embed?src={course.timetable_id}",
                        }
                    ],
                },
            },
            timeout=5,
        )
        if result.status_code != 200:  # noqa: PLR2004
            raise Exception(f"{course_name} not found in course info API")
