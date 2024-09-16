import argparse
import asyncio
import enum
import json
from pathlib import Path

from repositories.calendar import CalendarRepository
from repositories.course_info import CourseInfoRepository

from itmo_ai_timetable.logger import get_logger
from itmo_ai_timetable.repositories.db import DBRepository
from itmo_ai_timetable.schedule_parser import ScheduleParser
from itmo_ai_timetable.selection_parser import SelectionParser
from itmo_ai_timetable.transform_ics import export_ics

logger = get_logger(__name__)


class SubparserName(str, enum.Enum):
    SCHEDULE = "schedule"
    SELECTION = "selection"
    SYNC = "sync"


def create_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Обработка excel в ics")
    subparsers = parser.add_subparsers(required=True, dest="subparser_name")
    schedule_parser = subparsers.add_parser(SubparserName.SCHEDULE, help="Обработка excel в ics")
    schedule_parser.add_argument(
        "--filepath",
        help="Путь к файлу excel",
        default="Расписание 1 курс весна 2024.xlsx",
        type=str,
        required=True,
    )
    schedule_parser.add_argument("--output_path", help="Папка для экспорта ics", type=str)
    schedule_parser.add_argument("--sheet_name", help="Страница с расписанием в excel файле", type=str)
    schedule_parser.add_argument(
        "--db",
        help="Сохранить результат в db",
        action=argparse.BooleanOptionalAction,
        type=bool,
        default=False,
    )

    selection_parser = subparsers.add_parser(SubparserName.SELECTION, help="Обработка excel с выборностью")
    selection_parser.add_argument(
        "--filepath",
        help="Путь к файлу excel",
        default="Таблица предвыборности осень 2024 (2 курс).xlsx",
        type=str,
        required=True,
    )
    selection_parser.add_argument("--output_path", help="Папка для экспорта", default="ics", type=str)
    selection_parser.add_argument("--sheet_name", help="Страница с расписанием в excel файле", type=str)
    selection_parser.add_argument("--course_row", help="Строка с заголовками", type=int)
    selection_parser.add_argument("--first_select_column", help="Первый столбец с выборностью (AA)", type=str)
    selection_parser.add_argument("--last_select_column", help="Последний столбец с выборностью (AA)", type=str)
    selection_parser.add_argument("--name_column", help="Столбец с именами", default="A", type=str)
    selection_parser.add_argument("--course_number", help="Номер курса", default=2, type=int)
    selection_parser.add_argument(
        "--db",
        help="Сохранить результат в db",
        action=argparse.BooleanOptionalAction,
        type=bool,
        default=False,
    )
    subparsers.add_parser(SubparserName.SYNC, help="Обработка excel с выборностью")

    return parser.parse_args()


async def sync_calendar() -> None:
    courses = await DBRepository.get_courses()
    calendar = CalendarRepository()
    for course in courses:
        if course.timetable_id is None:
            calendar_id = calendar.get_or_create_calendar(course.name)
            course.timetable_id = calendar_id
        if course.course_info_link is None:
            course.course_info_link = CourseInfoRepository.add_link(course.name)
    await DBRepository.update_courses(courses)


async def main() -> None:
    logger.info("Start")
    args = create_args()

    output_path = Path(args.output_path)
    output_dir = output_path.parent
    if not Path.exists(output_dir):
        Path.mkdir(output_dir)
    match args.subparser_name:
        case SubparserName.SCHEDULE:
            schedule = ScheduleParser(args.filepath, args.sheet_name).parse()
            if args.db:
                _ = await DBRepository.add_classes(schedule)
            export_ics(schedule, output_dir)
        case SubparserName.SELECTION:
            results = SelectionParser(
                args.filepath,
                args.sheet_name,
                args.course_row,
                args.first_select_column,
                args.last_select_column,
                args.name_column,
            ).parse()
            with Path(output_path).open("w") as f:  # noqa: ASYNC230
                json.dump(results, f, ensure_ascii=False, indent=4)
            course_number = args.course_number
            if args.db:
                await DBRepository.create_matching(results, course_number)
        case SubparserName.SYNC:
            await sync_calendar()
        case _:
            raise ValueError(f"Unknown subparser {args.subparser}")
    logger.info(f"Files exported to {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
