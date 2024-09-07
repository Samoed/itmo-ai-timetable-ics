from collections import defaultdict

import openpyxl
from openpyxl.cell import MergedCell
from openpyxl.utils import column_index_from_string

from itmo_ai_timetable.cleaner import course_name_cleaner


class SelectionParser:
    def __init__(
        self,
        filepath: str,
        sheet_name: str,
        course_row: int,
        first_select_column: str,
        last_select_column: str,
        name_column: str = "A",
    ) -> None:
        self.workbook = openpyxl.load_workbook(filepath)
        self.sheet = self.workbook[sheet_name]
        self.course_row = course_row
        self.start_column = first_select_column
        self.end_column = last_select_column
        self.name_column = name_column
        self.data_start_row = course_row + 1

    def parse(self) -> dict[str, list[str | None]]:
        courses = self._get_courses()
        return self._match_names_to_courses(courses)

    def _get_courses(self) -> list[tuple[str, str]]:
        courses = []
        for cell in self.sheet[self.course_row]:
            if isinstance(cell, MergedCell):
                if cell.column <= column_index_from_string(
                    self.start_column,
                ) or cell.column >= column_index_from_string(self.end_column):
                    break
                raise ValueError(f"Cell {cell} is merged")
            if (
                column_index_from_string(self.start_column)
                <= column_index_from_string(cell.column_letter)
                <= column_index_from_string(self.end_column)
                and cell.value
                and isinstance(cell.value, str)
            ):
                courses.append((cell.column_letter, cell.value))
        return courses

    def _match_names_to_courses(self, courses: list[tuple[str, str]]) -> dict[str, list[str | None]]:
        matches = defaultdict(list)
        for row in self.sheet.iter_rows(min_row=self.data_start_row, min_col=1, max_col=1):
            name = row[0].value
            if name and isinstance(name, str):
                for col, course in courses:
                    cell_value = self.sheet[f"{col}{row[0].row}"].value
                    if cell_value == 1:
                        matches[name].append(course_name_cleaner(course))
        return matches
