from datetime import datetime
from pathlib import Path

from ics import Calendar, Event  # type: ignore[attr-defined]


def export_ics(df: list[tuple[datetime | None, datetime | None, str, str | None, str | None]], path: Path) -> None:
    unique_courses = {name for _, _, name, _, _ in df}
    for course in unique_courses:
        c = Calendar()

        for start, end, name, pair_type, link in df:
            if name != course:
                continue

            e = Event(
                name=name + (f" ({pair_type})" if pair_type else ""),
                begin=start,
                end=end,
                url=link,
                description=link,
            )
            c.events.add(e)

        with Path.open(path / f"{course}.ics", "w") as f:
            f.writelines(c.serialize())
