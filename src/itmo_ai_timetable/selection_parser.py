from collections import defaultdict

import openpyxl
from openpyxl.cell import MergedCell
from openpyxl.utils import column_index_from_string


class SelectionParser:
    def __init__(self, file_path: str):
        self.workbook = openpyxl.load_workbook(file_path)
        self.sheet = self.workbook.worksheets[1]
        self.course_row = 3
        self.start_column = "G"
        self.end_column = "BB"
        self.name_column = "A"
        self.data_start_row = 4

    def parse(self) -> dict[str, list[str]]:
        courses = self._get_courses()
        return self._match_names_to_courses(courses)

    def _get_courses(self) -> list[tuple[str, str]]:
        courses = []
        for cell in self.sheet[self.course_row]:
            if isinstance(cell, MergedCell):
                if cell.column <= column_index_from_string(
                    self.start_column
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

    def _match_names_to_courses(self, courses: list[tuple[str, str]]) -> dict[str, list[str]]:
        matches = defaultdict(list)
        for row in self.sheet.iter_rows(min_row=self.data_start_row, min_col=1, max_col=1):
            name = row[0].value
            if name and isinstance(name, str):
                for col, course in courses:
                    cell_value = self.sheet[f"{col}{row[0].row}"].value
                    if cell_value == 1:
                        matches[name].append(course)
        return matches
