from datetime import datetime

from ics import Calendar, Event  # type: ignore[attr-defined]


def export_ics(df: list[tuple[datetime, datetime, str, str | None, str | None]], path: str) -> None:
    unique_courses = {name for _, _, name, _, _ in df}
    for course in unique_courses:
        c = Calendar()

        for start, end, name, pair_type, link in df:
            if not (name == course or name[:-3] == course or name[:-4] == course):
                continue

            e = Event(
                name=name + (f" ({pair_type})" if pair_type else ""),
                begin=start,
                end=end,
                url=link,
                description=link,
            )
            c.events.add(e)

        with open(f"{path}/{course}.ics", "w") as f:
            f.writelines(c.serialize())
