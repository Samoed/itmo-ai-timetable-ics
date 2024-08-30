from sqlalchemy import select

from itmo_ai_timetable.db.base import Course


async def test_create_course(session):
    course = Course(name="test_course")
    session.add(course)
    await session.commit()
    course = (await session.execute(select(Course))).scalar()
    assert course.name == "test_course"
