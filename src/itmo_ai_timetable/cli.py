import argparse
import asyncio
import enum
import json
from pathlib import Path

from repository import Repository

from itmo_ai_timetable.logger import get_logger
from itmo_ai_timetable.schedule_parser import ScheduleParser
from itmo_ai_timetable.selection_parser import SelectionParser
from itmo_ai_timetable.transform_ics import export_ics

logger = get_logger(__name__)


class SubparserName(str, enum.Enum):
    SCHEDULE = "schedule"
    SELECTION = "selection"


def create_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Обработка excel в ics")
    subparsers = parser.add_subparsers(required=True, dest="subparser_name")
    schedule_parser = subparsers.add_parser(SubparserName.SCHEDULE, help="Обработка excel в ics")
    schedule_parser.add_argument(
        "--filepath", help="Путь к файлу excel", default="Расписание 1 курс весна 2024.xlsx", type=str
    )
    schedule_parser.add_argument("--output_path", help="Папка для экспорта ics", default="ics", type=str)
    schedule_parser.add_argument("--sheet", help="Страница с расписанием в excel файле", default=0, type=int)

    selection_parser = subparsers.add_parser(SubparserName.SELECTION, help="Обработка excel с выборностью")
    selection_parser.add_argument(
        "--filepath", help="Путь к файлу excel", default="Таблица предвыборности осень 2024 (2 курс).xlsx", type=str
    )
    selection_parser.add_argument("--output_path", help="Папка для экспорта ics", default="ics", type=str)
    selection_parser.add_argument("--sheet_name", help="Страница с расписанием в excel файле", type=str)
    selection_parser.add_argument("--course_row", help="Строка с заголовками", type=int)
    selection_parser.add_argument("--first_select_column", help="Первый столбец с выборностью (AA)", type=str)
    selection_parser.add_argument("--last_select_column", help="Последний столбец с выборностью (AA)", type=str)
    selection_parser.add_argument("--name_column", help="Столбец с именами", default="A", type=str)
    selection_parser.add_argument("--course_number", help="Номер курса", default=2, type=int)
    selection_parser.add_argument(
        "--db", help="Сохранить результат в db", action=argparse.BooleanOptionalAction, type=bool, default=False
    )
    return parser.parse_args()


async def main() -> None:
    logger.info("Start")
    args = create_args()

    output_path = Path(args.output_path)
    output_dir = output_path.parent
    if not Path.exists(output_dir):
        Path.mkdir(output_dir)
    match args.subparser_name:
        case SubparserName.SCHEDULE:
            df = ScheduleParser(args.filepath, args.sheet_num).parse()
            export_ics(df, output_path)
        case SubparserName.SELECTION:
            results = SelectionParser(
                args.filepath,
                args.sheet_name,
                args.course_row,
                args.first_select_column,
                args.last_select_column,
                args.name_column,
            ).parse()
            with Path(output_path).open("w") as f:
                json.dump(results, f, ensure_ascii=False, indent=4)
            course_number = args.course_number
            if args.db:
                await Repository.create_matching(results, course_number)
        case _:
            raise ValueError(f"Unknown subparser {args.subparser}")
    logger.info(f"Files exported to {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
