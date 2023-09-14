import argparse
import os

from src.logger import get_logger
from src.timetable_file import TimetableFile
from src.transform_ics import export_ics

logger = get_logger(__name__)


def parse_arguments() -> tuple[str, str, int]:
    parser = argparse.ArgumentParser(description="Обработка excel в ics")
    parser.add_argument("--file", help="Путь к файлу excel", default="../Расписание 1 курс 23_24.xlsx", type=str)
    parser.add_argument("--output", help="Папка для экспорта ics", default="../ics", type=str)
    parser.add_argument("--sheet", help="Страница с расписанием в excel файле", default=1, type=int)
    args = parser.parse_args()
    return args.file, args.output, args.sheet


def main() -> None:
    logger.info("Start")
    filepath, output_path, sheet_num = parse_arguments()
    timetable = TimetableFile(filepath, sheet_num)
    df = timetable.parse()
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    export_ics(df, output_path)
    logger.info(f"Files exported to {output_path}")


if __name__ == "__main__":
    main()
