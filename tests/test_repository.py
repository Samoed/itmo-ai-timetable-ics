from datetime import datetime

from dateutil import tz
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from itmo_ai_timetable.db.base import Class, ClassStatusTable, Course
from itmo_ai_timetable.repository import Repository
from itmo_ai_timetable.schemes import ClassStatus, Pair

tzinfo = tz.gettz("Europe/Moscow")


async def test_get_class_status_by_name(session: AsyncSession):
    synced_status = await Repository.get_class_status_by_name(ClassStatus.synced, session=session)

    result = await Repository.get_class_status_by_name(ClassStatus.synced, session=session)
    assert result.id == synced_status.id


async def test_get_or_create_course_existing(session: AsyncSession):
    course_name = "Existing Course"
    existing_course = Course(name=course_name)
    session.add(existing_course)
    await session.commit()

    result = await Repository.get_or_create_course(course_name, session)

    assert result.id == existing_course.id
    assert result.name == course_name


async def test_get_or_create_course_new(session: AsyncSession):
    course_name = "New Course"

    result = await Repository.get_or_create_course(course_name, session)

    assert result.id is not None
    assert result.name == course_name

    # Verify the course was added to the database
    db_course = await session.get(Course, result.id)
    assert db_course is not None
    assert db_course.name == course_name


async def test_get_existing_classes(session: AsyncSession):
    synced = await Repository.get_class_status_by_name(ClassStatus.synced, session=session)
    need_to_delete = await Repository.get_class_status_by_name(ClassStatus.need_to_delete, session=session)

    course = Course(name="Test Course")
    session.add(course)
    await session.flush()

    classes = [
        Class(
            course_id=course.id,
            start_time=datetime(2023, 1, 1, 9, 0, tzinfo=tzinfo),
            end_time=datetime(2023, 1, 1, 10, 30, tzinfo=tzinfo),
            class_status=synced,
        ),
        Class(
            course_id=course.id,
            start_time=datetime(2023, 1, 1, 11, 0, tzinfo=tzinfo),
            end_time=datetime(2023, 1, 1, 12, 30, tzinfo=tzinfo),
            class_status=synced,
        ),
        Class(
            course_id=course.id,
            start_time=datetime(2023, 1, 1, 13, 0, tzinfo=tzinfo),
            end_time=datetime(2023, 1, 1, 14, 30, tzinfo=tzinfo),
            class_status=need_to_delete,
        ),
    ]
    session.add_all(classes)
    await session.commit()

    # Act
    result = await Repository.get_existing_classes(course.id, synced, session)

    # Assert
    assert len(result) == 2
    assert all(c.class_status.id == synced.id for c in result)


async def test_update_class_statuses(session: AsyncSession):
    synced = await Repository.get_class_status_by_name(ClassStatus.synced, session=session)
    need_to_delete = await Repository.get_class_status_by_name(ClassStatus.need_to_delete, session=session)
    course = Course(name="Test Course")
    session.add(course)
    await session.flush()

    classes = [
        Class(
            course_id=course.id,
            start_time=datetime(2023, 1, 1, 9, 0, tzinfo=tzinfo),
            end_time=datetime(2023, 1, 1, 10, 30, tzinfo=tzinfo),
            class_status=synced,
        ),
        Class(
            course_id=course.id,
            start_time=datetime(2023, 1, 1, 11, 0, tzinfo=tzinfo),
            end_time=datetime(2023, 1, 1, 12, 30, tzinfo=tzinfo),
            class_status=synced,
        ),
    ]
    session.add_all(classes)
    await session.commit()

    await Repository.update_class_statuses(classes, need_to_delete)
    await session.commit()

    for class_obj in classes:
        assert class_obj.class_status_id == need_to_delete.id


async def test_add_classes_new_course(session: AsyncSession):
    start_time = datetime(2023, 1, 1, 9, 0, tzinfo=tzinfo)
    end_time = datetime(2023, 1, 1, 10, 30, tzinfo=tzinfo)
    classes = [
        Pair(
            name="Math",
            start_time=start_time,
            end_time=end_time,
            pair_type="Lecture",
            link=None,
        )
    ]

    await Repository.add_classes(classes, session=session)

    result = await session.execute(select(Course).where(Course.name == "Math"))
    course = result.scalar_one()
    assert course is not None
    assert course.name == "Math"

    result = await session.execute(select(Class).where(Class.course_id == course.id))
    class_obj = result.scalar_one()
    assert class_obj is not None
    assert class_obj.start_time == start_time
    assert class_obj.end_time == end_time
    class_status = (
        await session.execute(select(ClassStatusTable).where(ClassStatusTable.id == class_obj.class_status_id))
    ).scalar_one()
    assert class_status.name == ClassStatus.need_to_add.name


async def test_add_classes_existing_course(session: AsyncSession):
    course = Course(name="Physics")
    session.add(course)
    await session.commit()

    start_time = datetime(2023, 1, 1, 9, 0, tzinfo=tzinfo)
    end_time = datetime(2023, 1, 1, 10, 30, tzinfo=tzinfo)

    classes = [
        Pair(
            name="Physics",
            start_time=start_time,
            end_time=end_time,
            pair_type="Lecture",
            link=None,
        )
    ]

    await Repository.add_classes(classes, session=session)

    result = await session.execute(select(Class).where(Class.course_id == course.id))
    class_obj = result.scalar_one()
    assert class_obj is not None
    assert class_obj.start_time == start_time
    assert class_obj.end_time == end_time


async def test_add_classes_update_existing(session: AsyncSession):
    course = Course(name="Chemistry")
    session.add(course)
    await session.commit()

    synced_status = await Repository.get_class_status_by_name(ClassStatus.synced, session=session)

    start_time = datetime(2023, 1, 1, 13, 0, tzinfo=tzinfo)
    end_time = datetime(2023, 1, 1, 14, 30, tzinfo=tzinfo)

    existing_class = Class(
        course_id=course.id,
        start_time=start_time,
        end_time=end_time,
        class_status_id=synced_status.id,
    )
    session.add(existing_class)
    await session.commit()

    classes = [
        Pair(
            name="Chemistry",
            start_time=start_time,
            end_time=end_time,
            pair_type="Lab",
            link=None,
        )
    ]

    await Repository.add_classes(classes, session=session)

    result = await session.execute(select(Class).where(Class.course_id == course.id))
    class_obj = result.scalar_one()
    assert class_obj is not None
    assert class_obj.start_time == start_time
    assert class_obj.end_time == end_time
    assert class_obj.class_status_id == synced_status.id


async def test_add_classes_delete_existing(session: AsyncSession):
    course = Course(name="Biology")
    session.add(course)
    await session.commit()
    synced_status = await Repository.get_class_status_by_name(ClassStatus.synced, session=session)
    added_status = await Repository.get_class_status_by_name(ClassStatus.need_to_add, session=session)
    deleted_status = await Repository.get_class_status_by_name(ClassStatus.need_to_delete, session=session)

    existing_class = Class(
        course_id=course.id,
        start_time=datetime(2023, 1, 1, 15, 0, tzinfo=tzinfo),
        end_time=datetime(2023, 1, 1, 16, 30, tzinfo=tzinfo),
        class_status_id=synced_status.id,
    )
    session.add(existing_class)
    await session.commit()

    classes = [
        Pair(
            name="Biology",
            start_time=datetime(2023, 1, 1, 16, 0, tzinfo=tzinfo),
            end_time=datetime(2023, 1, 1, 17, 30, tzinfo=tzinfo),
            pair_type="Seminar",
            link=None,
        )
    ]

    await Repository.add_classes(classes, session=session)

    result = await session.execute(select(Class).where(Class.course_id == course.id))
    classes = result.scalars().all()
    assert len(classes) == 2

    deleted_class = next(c for c in classes if c.start_time == datetime(2023, 1, 1, 15, 0, tzinfo=tzinfo))
    assert deleted_class.class_status_id == deleted_status.id

    new_class = next(c for c in classes if c.start_time == datetime(2023, 1, 1, 16, 0, tzinfo=tzinfo))
    assert new_class.class_status_id == added_status.id


async def test_add_classes_multiple_courses(session: AsyncSession):
    classes = [
        Pair(
            name="Math",
            start_time=datetime(2023, 1, 1, 9, 0, tzinfo=tzinfo),
            end_time=datetime(2023, 1, 1, 10, 30, tzinfo=tzinfo),
        ),
        Pair(
            name="Physics",
            start_time=datetime(2023, 1, 1, 11, 0, tzinfo=tzinfo),
            end_time=datetime(2023, 1, 1, 12, 30, tzinfo=tzinfo),
        ),
        Pair(
            name="Math",
            start_time=datetime(2023, 1, 1, 13, 0, tzinfo=tzinfo),
            end_time=datetime(2023, 1, 1, 14, 30, tzinfo=tzinfo),
        ),
    ]

    await Repository.add_classes(classes, session=session)

    result = await session.execute(select(Course))
    courses = result.scalars().all()
    assert len(courses) == 2

    result = await session.execute(select(Class))
    classes = result.scalars().all()
    assert len(classes) == 3


async def test_add_classes(session: AsyncSession):
    need_to_add = await Repository.get_class_status_by_name(ClassStatus.need_to_add, session=session)
    need_to_delete = await Repository.get_class_status_by_name(ClassStatus.need_to_delete, session=session)
    synced = await Repository.get_class_status_by_name(ClassStatus.synced, session=session)

    pairs = [
        Pair(
            name="Math",
            start_time=datetime(2023, 1, 1, 9, 0, tzinfo=tzinfo),
            end_time=datetime(2023, 1, 1, 10, 30, tzinfo=tzinfo),
            pair_type="Lecture",
        ),
        Pair(
            name="Physics",
            start_time=datetime(2023, 1, 1, 11, 0, tzinfo=tzinfo),
            end_time=datetime(2023, 1, 1, 12, 30, tzinfo=tzinfo),
            pair_type="Lab",
        ),
        Pair(
            name="Math",
            start_time=datetime(2023, 1, 1, 13, 0, tzinfo=tzinfo),
            end_time=datetime(2023, 1, 1, 14, 30, tzinfo=tzinfo),
            pair_type="Seminar",
        ),
    ]

    # Add an existing class that should be marked for deletion
    math_course = Course(name="Math")
    existing_class = Class(
        course=math_course,
        start_time=datetime(2023, 1, 1, 15, 0, tzinfo=tzinfo),
        end_time=datetime(2023, 1, 1, 16, 30, tzinfo=tzinfo),
        class_status=synced,
    )
    session.add(existing_class)
    await session.commit()

    await Repository.add_classes(pairs, session=session)

    courses = (await session.execute(select(Course))).scalars().all()
    assert len(courses) == 2
    assert {c.name for c in courses} == {"Math", "Physics"}

    classes = (await session.execute(select(Class))).scalars().all()
    assert len(classes) == 4  # 3 new classes + 1 existing class marked for deletion

    new_classes = [c for c in classes if c.class_status_id == need_to_add.id]
    assert len(new_classes) == 3
    assert all(c.class_status_id == need_to_add.id for c in new_classes)

    deleted_class = next(c for c in classes if c.class_status_id == need_to_delete.id)
    assert deleted_class.start_time == datetime(2023, 1, 1, 15, 0, tzinfo=tzinfo)
    assert deleted_class.end_time == datetime(2023, 1, 1, 16, 30, tzinfo=tzinfo)
