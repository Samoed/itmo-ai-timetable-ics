from datetime import datetime

import openpyxl
import pytz
from openpyxl.cell.cell import Cell, MergedCell
from openpyxl.worksheet.merge import MergedCellRange

from src.logger import get_logger

logger = get_logger(__name__)
moscow_tz = pytz.timezone("Europe/Moscow")


class TimetableFile:
    DAYS_COLUMN = 2  # Column B
    TIMETABLE_OFFSET = 3  # Offset between date and timetable
    TIMETABLE_LEN = 5  # Length of timetable

    def __init__(self, path: str, sheet: int):
        logger.info(f"Open file {path}")
        wb = openpyxl.load_workbook(path)
        self.sheet = wb.worksheets[sheet]

    def _get_days(self) -> list[MergedCellRange]:
        days_cells = []

        for merged_cell_range in self.sheet.merged_cells.ranges:
            if merged_cell_range.min_col == self.DAYS_COLUMN and merged_cell_range.max_col == self.DAYS_COLUMN:
                days_cells.append(merged_cell_range)
        return days_cells

    def find_mergedcell_mergerange(self, merged_cell: MergedCell) -> MergedCellRange:
        for merged_range in self.sheet.merged_cells.ranges:
            if (
                merged_range.min_col <= merged_cell.column <= merged_range.max_col
                and merged_range.min_row <= merged_cell.row <= merged_range.max_row
            ):
                return merged_range

    def get_first_cell_from_mergedcell_range(self, cell_range: MergedCellRange) -> Cell:
        for cell in cell_range.cells:
            return self.sheet.cell(row=cell[0], column=cell[1])

    def find_mergedcell_bounds(self, merged_cell: MergedCell) -> tuple[int, int, int, int]:
        merged_range = self.find_mergedcell_mergerange(merged_cell)
        return (
            merged_range.min_row,
            merged_range.min_col,
            merged_range.max_row,
            merged_range.max_col,
        )

    def pair_time(self, cell: Cell, day: datetime) -> tuple[datetime, datetime]:
        time = cell.value
        start_time, end_time = time.split("-")
        start_hour, start_minute = map(int, start_time.split(":"))
        end_hour, end_minute = map(int, end_time.split(":"))
        pair_start = day.replace(hour=start_hour, minute=start_minute).astimezone(pytz.timezone("Europe/Moscow"))
        pair_end = day.replace(hour=end_hour, minute=end_minute).astimezone(pytz.timezone("Europe/Moscow"))
        return pair_start, pair_end

    def process_cell(self, cell: Cell | MergedCell) -> tuple[str, str | None]:
        if cell.value is not None:
            link = None if cell.hyperlink is None else cell.hyperlink.target
            # Иностранный язык \nУровни А1/А2 breaking export
            return cell.value.replace("/", "\\"), link

        if type(cell) is MergedCell:
            merge_range = self.find_mergedcell_mergerange(cell)
            first_cell = self.get_first_cell_from_mergedcell_range(merge_range)
            link = None if first_cell.hyperlink is None else first_cell.hyperlink.target
            return first_cell.value.replace("/", "\\"), link

        return "", None

    def parse(self) -> list[tuple[datetime, datetime, str, str | None]]:
        logger.info("Start parse")
        df = []
        pair_start = datetime.now()
        pair_end = datetime.now()
        for day_cell in self._get_days():
            day = self.get_first_cell_from_mergedcell_range(day_cell).value

            for row in self.sheet.iter_rows(
                min_row=day_cell.min_row,
                max_row=day_cell.max_row,
                min_col=day_cell.min_col + self.TIMETABLE_OFFSET,
                max_col=day_cell.max_col + self.TIMETABLE_OFFSET + self.TIMETABLE_LEN,
            ):
                for cell_num, cell in enumerate(row):
                    if cell_num == 0:  # get time for row
                        pair_start, pair_end = self.pair_time(cell, day)
                        continue
                    title, link = self.process_cell(cell)
                    if title != "":
                        df.append((pair_start, pair_end, title, link))
        logger.info("End parse")
        return df
