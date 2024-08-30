import argparse
import enum
import json
from pathlib import Path

from itmo_ai_timetable.logger import get_logger
from itmo_ai_timetable.schedule_parser import ScheduleParser
from itmo_ai_timetable.selection_parser import SelectionParser
from itmo_ai_timetable.transform_ics import export_ics

logger = get_logger(__name__)


class SubparserName(str, enum.Enum):
    SCHEDULE = "schedule"
    SELECTION = "selection"


def create_args() -> tuple[SubparserName, str, str, int]:
    parser = argparse.ArgumentParser(description="Обработка excel в ics")
    subparsers = parser.add_subparsers(required=True, dest="subparser_name")
    schedule_parser = subparsers.add_parser(SubparserName.SCHEDULE, help="Обработка excel в ics")
    schedule_parser.add_argument(
        "--file", help="Путь к файлу excel", default="Расписание 1 курс весна 2024.xlsx", type=str
    )
    schedule_parser.add_argument("--output", help="Папка для экспорта ics", default="ics", type=str)
    schedule_parser.add_argument("--sheet", help="Страница с расписанием в excel файле", default=0, type=int)

    selection_parser = subparsers.add_parser(SubparserName.SELECTION, help="Обработка excel с выборностью")
    selection_parser.add_argument(
        "--file", help="Путь к файлу excel", default="Таблица предвыборности осень 2024 (2 курс).xlsx", type=str
    )
    selection_parser.add_argument("--output", help="Папка для экспорта ics", default="ics", type=str)
    selection_parser.add_argument("--sheet", help="Страница с расписанием в excel файле", default=0, type=int)

    args = parser.parse_args()
    return args.subparser_name, args.file, args.output, args.sheet


def main() -> None:
    logger.info("Start")
    subparser, filepath, output_path_str, sheet_num = create_args()
    output_path = Path(output_path_str)
    if not Path.exists(output_path):
        Path.mkdir(output_path)
    match subparser:
        case SubparserName.SCHEDULE:
            df = ScheduleParser(filepath, sheet_num).parse()
            export_ics(df, output_path)
        case SubparserName.SELECTION:
            results = SelectionParser(filepath).parse()
            with Path(output_path / "selection.json").open("w") as f:
                json.dump(results, f)
        case _:
            raise ValueError(f"Unknown subparser {subparser}")
    logger.info(f"Files exported to {output_path}")


if __name__ == "__main__":
    main()
