from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from itmo_ai_timetable.db.base import Class, ClassStatus, Course, User
from itmo_ai_timetable.db.session_manager import with_async_session
from itmo_ai_timetable.schemes import Pair


class Repository:
    @staticmethod
    @with_async_session
    async def add_classes(classes: list[Pair], session: AsyncSession) -> None:
        courses_names = {c.name for c in classes}
        for course_name in courses_names:
            course = (await session.execute(select(Course).filter(Course.name == course_name))).scalar()
            if course is None:
                course = Course(name=course_name)
                session.add(course)
                await session.commit()
            existing_classes = (
                await session.execute(
                    select(Class).filter(
                        and_(Class.course_id == course.id, Class.class_status_id == ClassStatus.synced)
                    )
                )
            ).scalars()
            existing_classes_identifiers = {(c.start_time, c.end_time) for c in classes}

            new_classes_identifiers = {(c.start_time, c.end_time) for c in existing_classes}

            classes_to_add = [c for c in classes if (c.start_time, c.end_time) in existing_classes_identifiers]

            classes_to_delete = [
                c for c in existing_classes if (c.start_time, c.end_time) not in new_classes_identifiers
            ]

            for class_to_delete in classes_to_delete:
                for existing_class in existing_classes:
                    if (
                        class_to_delete.start_time == existing_class.start_time
                        and class_to_delete.end_time == existing_class.end_time
                    ):
                        existing_class.class_status = ClassStatus.need_to_delete

            for class_to_add in classes_to_add:
                session.add(
                    Class(course_id=course.id, start_time=class_to_add.start_time, end_time=class_to_add.end_time)
                )

            await session.commit()

    @staticmethod
    @with_async_session
    async def get_unsynced_classes(session: AsyncSession) -> list[tuple[Class, Course]]:
        result = await session.execute(
            select(Class, Course)
            .join(Course, Class.course_id == Course.id)
            .filter(Class.class_status != ClassStatus.synced)
        )
        return result.all()

    @staticmethod
    @with_async_session
    async def create_matching(selected: dict[str, list[str]], session: AsyncSession) -> None:
        """

        :param selected: contains pairs of names of users and courses he selected
        :param session:
        :return:
        """
        for user_name, courses in selected.items():
            user = (await session.execute(select(User).filter(User.user_real_name == user_name))).scalar()
            if user is None:
                user = User(user_real_name=user_name)
                session.add(user)
                await session.commit()
            for course_name in courses:
                course = (await session.execute(select(Course).filter(Course.name == course_name))).scalar()
                if course is None:
                    raise ValueError(f"Course {course_name} not found")
                user.courses.append(course)
            await session.commit()
