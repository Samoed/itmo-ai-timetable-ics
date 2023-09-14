from datetime import datetime

from ics import Calendar, Event  # type: ignore[attr-defined]


def export_ics(df: list[tuple[datetime, datetime, str, str | None]], path: str) -> None:
    unique_courses = {name for _, _, name, _ in df if not name.endswith(" ПА") and not name.endswith(" ПА\n")}
    for course in unique_courses:
        c = Calendar()

        for start, end, name, link in df:
            if name != course or name[:-3] != course or name[:-4] != course:
                continue

            e = Event(
                name=name,
                begin=start,
                end=end,
                url=link,
                description=link,
            )
            c.events.add(e)

        with open(f"{path}/{course}.ics", "w") as f:
            f.writelines(c.serialize())
