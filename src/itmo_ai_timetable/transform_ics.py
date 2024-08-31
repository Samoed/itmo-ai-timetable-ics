from pathlib import Path

from ics import Calendar, Event  # type: ignore

from itmo_ai_timetable.schemes import Pair


def export_ics(pairs: list[Pair], path: Path) -> None:
    unique_courses = {p.name for p in pairs}
    for course in unique_courses:
        c = Calendar()

        for pair in pairs:
            if pair.name != course:
                continue

            e = Event(
                name=pair.name + (f" ({pair.pair_type})" if pair.pair_type else ""),
                begin=pair.start_time,
                end=pair.end_time,
                url=pair.link,
                description=pair.link,
            )
            c.events.add(e)

        with Path.open(path / f"{course}.ics", "w") as f:
            f.writelines(c.serialize())
