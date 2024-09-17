from collections import defaultdict
from collections.abc import Sequence

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from itmo_ai_timetable.db.base import Class, ClassStatusTable, Course, User
from itmo_ai_timetable.db.session_manager import with_async_session
from itmo_ai_timetable.schemes import ClassStatus, Pair


class DBRepository:
    @staticmethod
    @with_async_session
    async def get_class_status_by_name(class_status: ClassStatus, *, session: AsyncSession) -> ClassStatusTable:
        result = await session.execute(select(ClassStatusTable).filter(ClassStatusTable.name == class_status.name))
        return result.scalar_one()

    @staticmethod
    async def get_course(course_name: str, session: AsyncSession) -> Course | None:
        query = await session.execute(select(Course).filter(Course.name == course_name))
        return query.scalar()

    @staticmethod
    @with_async_session
    async def get_courses(*, session: AsyncSession) -> Sequence[Course]:
        query = select(Course)
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    @with_async_session
    async def update_courses(courses: list[Course], *, session: AsyncSession) -> None:
        session.add_all(courses)
        await session.commit()

    @staticmethod
    @with_async_session
    async def update_classes(classes: list[Class], *, session: AsyncSession) -> None:
        session.add_all(classes)
        await session.commit()

    @staticmethod
    async def get_existing_classes(
        course_id: int,
        synced_status: ClassStatusTable,
        session: AsyncSession,
    ) -> Sequence[Class]:
        query = select(Class).filter(and_(Class.course_id == course_id, Class.class_status == synced_status))
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def update_class_statuses(classes_to_delete: list[Class], need_to_delete_status: ClassStatusTable) -> None:
        for class_obj in classes_to_delete:
            class_obj.class_status = need_to_delete_status

    @staticmethod
    async def create_new_classes(course_id: int, classes_to_add: list[Pair]) -> list[Class]:
        return [
            Class(course_id=course_id, start_time=c.start_time, end_time=c.end_time, class_type=c.pair_type)
            for c in classes_to_add
        ]

    @staticmethod
    @with_async_session
    async def add_classes(classes: list[Pair], *, session: AsyncSession) -> list[str]:
        synced_status = await DBRepository.get_class_status_by_name(ClassStatus.synced, session=session)
        need_to_delete_status = await DBRepository.get_class_status_by_name(ClassStatus.need_to_delete, session=session)

        courses_classes = defaultdict(list)
        for c in classes:
            courses_classes[c.name].append(c)

        not_found_courses = []
        for course_name, course_classes in courses_classes.items():
            course = await DBRepository.get_course(course_name, session)

            if course is None:
                not_found_courses.append(course_name)
                continue

            existing_classes = await DBRepository.get_existing_classes(course.id, synced_status, session)
            existing_class_identifiers = {(c.start_time, c.end_time) for c in existing_classes}
            new_class_identifiers = {(c.start_time, c.end_time) for c in course_classes}

            classes_to_add = [c for c in course_classes if (c.start_time, c.end_time) not in existing_class_identifiers]
            classes_to_delete = [c for c in existing_classes if (c.start_time, c.end_time) not in new_class_identifiers]

            await DBRepository.update_class_statuses(classes_to_delete, need_to_delete_status)
            new_classes = await DBRepository.create_new_classes(course.id, classes_to_add)

            session.add_all(new_classes)

        await session.commit()
        return list(set(not_found_courses))

    @staticmethod
    @with_async_session
    async def get_or_create_user(user_name: str, course_number: int, *, session: AsyncSession) -> User:
        query = await session.execute(
            select(User).filter(and_(User.user_real_name == user_name, User.studying_course == course_number)),
        )
        user = query.scalar()
        if user is None:
            user = User(user_real_name=user_name, studying_course=course_number)
            session.add(user)
            await session.commit()
        return user

    @staticmethod
    @with_async_session
    async def create_matching(selected: dict[str, list[str]], course_number: int, *, session: AsyncSession) -> None:
        """
        :param selected: contains pairs of names of users and courses he selected
        :param course_number: number of course
        :param session:
        :return:
        """
        for user_name, courses in selected.items():
            user = await DBRepository.get_or_create_user(user_name, course_number, session=session)
            for course_name in courses:
                course = await DBRepository.get_course(course_name, session)
                # Fetch the user's current courses
                await session.refresh(user, ["courses"])

                if course is None:
                    raise ValueError(f"Course {course_name} not found")

                if course not in user.courses:
                    user.courses.append(course)

                await session.commit()

    @staticmethod
    @with_async_session
    async def set_gcal_id_to_course(course_name: str, gcal_id: str, *, session: AsyncSession) -> None:
        course = await DBRepository.get_course(course_name, session)
        course.gcal_id = gcal_id
        await session.commit()

    @staticmethod
    @with_async_session
    async def get_unsynced_classes_for_course(course: Course, *, session: AsyncSession) -> Sequence[Class]:
        synced_status = await DBRepository.get_class_status_by_name(ClassStatus.synced, session=session)
        query = select(Class).filter(and_(Class.course_id == course.id, Class.class_status != synced_status))
        result = await session.execute(query)
        return result.scalars().all()
