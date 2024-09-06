import json

import pandas as pd

notion_file = "notion.csv"
timetable_file = "Расписание.xlsx"
preselection_file = "Таблица предвыборности.xlsx"


def standardize_course_name(course):
    if not isinstance(course, str):
        return None

    course = course.strip()

    for check in (
        "Выходной",
        "Хакатон",
        "Demoday",
        "Количество выбранных курсов",
        "Вариант обучения",
        "Преподаватель:",
    ):
        if check in course:
            return None

    if any(keyword in course for keyword in ["Экзамен", "Лекция", "Зачет"]):
        return None

    if "\n" in course:
        course = course.split("\n")[0].strip()

    replacements = {
        "A/B тестирование": "А/В тестирование",
        "Управление RnD командами": "Проведение научных исследований в области ИИ (Управление RnD командами)",
        "Проведение научных исследований в области ИИ": (
            "Проведение научных исследований в области ИИ (Управление RnD командами)"
        ),
        "Этика ИИ": "Этика искусственного интеллекта",
        "Системы обработки и анализа больших массивов данных (VK)": (
            "Системы обработки и анализа больших массивов данных"
        ),
        "Симулятор DS от Karpov.courses": "Симулятор DS от Karpov.Courses",
        "DS симулятор от Karpov.courses": "Симулятор DS от Karpov.Courses",
        "Программирование на С++": ["C++ Lite", "C++ Hard"],
        "Uplift-моделирование": "UPLIFT-моделирование",
        "Продвинутое A/B-тестирование": "Продвинутое А/B - тестирование",
        "А/В тестирование и Reliable ML": "А/В тестирование",
        "Построение баз данных": "Построение БД",
        "Введение в большие языковые модели (LLM)": "Введение в LLM",
        "Создание технологического бизнеса: чек-лист для предпринимателей": "Создание технологического бизнеса",
        (
            "High Tech Business Creation: check-list for entrepreneurs"
            " / Создание технологического бизнеса: чек-лист для предпринимателей"
        ): "Создание технологического бизнеса",
        "Воркшоп по разработке автономного агента на основе LLM (Осенний семестр)": (
            "Воркшоп по разработке автономного агента на основе LLM"
        ),
    }

    if course in replacements:
        return replacements[course]

    return course


def timetable_parser(timetable_filename: str):
    df = pd.read_excel(timetable_filename, sheet_name="Расписание")
    timetable = df.iloc[2:, 5:10].to_numpy().flatten()
    t = pd.Series(timetable)
    full_courses = set(t[pd.notna(t)].tolist())
    return set(filter(None, map(standardize_course_name, full_courses)))


def preselection_parser(preselection_filename: str, preselection_params):
    df = pd.read_excel(preselection_filename, sheet_name=preselection_params["name"])
    courses_row = df.iloc[1, 4:-5]
    courses = set(courses_row.tolist())
    return set(filter(None, map(standardize_course_name, courses)))


def notion_parser(notion_filename: str) -> set[str]:
    df = pd.read_csv(notion_filename)
    courses = df["Курсы"].tolist()
    standardized_courses = []
    for course in map(standardize_course_name, courses):
        if isinstance(course, list):
            standardized_courses.extend(course)
        elif course:
            standardized_courses.append(course)
    return set(standardized_courses)


def main(course_folder: str, preselection_params):
    notion_courses = notion_parser(course_folder + notion_file)
    timetable_courses = timetable_parser(course_folder + timetable_file)
    preselection_courses = preselection_parser(course_folder + preselection_file, preselection_params)

    for name, courses in [
        ("notion", notion_courses),
        ("timetable", timetable_courses),
        ("preselection", preselection_courses),
    ]:
        with open(f"{course_folder}{name}_courses.json", "w", encoding="utf-8") as f:
            json.dump(list(courses), f, ensure_ascii=False)

    print("course folder", course_folder)
    print("notion", notion_courses)
    print("Courses in preselection, but not in notion", preselection_courses - notion_courses)
    print("Courses in timetable, but not in notion", timetable_courses - notion_courses)
    print("Courses in timetable, but not in preselection", timetable_courses - preselection_courses)
    return notion_courses, timetable_courses, preselection_courses


if __name__ == "__main__":
    course_1 = main("course_1/", {"name": "Таблица предвыборности"})
    course_2 = main("course_2/", {"name": "Таблица выборности"})
    total_courses = set().union(*course_1, *course_2)
    with open("total_courses.json", "w", encoding="utf-8") as f:
        json.dump(sorted(total_courses), f, ensure_ascii=False, indent=4)