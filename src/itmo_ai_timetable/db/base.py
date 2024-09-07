from datetime import datetime
from typing import Any, ClassVar

from sqlalchemy import TIMESTAMP, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql.type_api import TypeEngine

from itmo_ai_timetable.schemes import ClassStatus


class Base(DeclarativeBase):
    type_annotation_map: ClassVar[dict[Any, TypeEngine[Any]]] = {
        datetime: TIMESTAMP(timezone=True),
    }


class Course(Base):
    __tablename__ = "course"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    meeting_link: Mapped[str] = mapped_column(nullable=True)
    course_info_link: Mapped[str] = mapped_column(nullable=True)
    chat_link: Mapped[str] = mapped_column(nullable=True)
    timetable_id: Mapped[str] = mapped_column(nullable=True)

    # many-to-many relationship to User, bypassing the `UserCourse` class
    students: Mapped[list["User"]] = relationship(secondary="user_course", back_populates="courses", viewonly=True)

    # association between Course -> UserCourse -> User
    student_enrollments: Mapped[list["UserCourse"]] = relationship(back_populates="course")
    classes: Mapped[list["Class"]] = relationship("Class", back_populates="course")

    def __repr__(self) -> str:
        return (
            f"<Course(id={self.id}, name={self.name}, meeting_link={self.meeting_link}, "
            f"notion_link={self.course_info_link}, tg_chat_link={self.chat_link}, timetable_id={self.timetable_id})>"
        )


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_real_name: Mapped[str] = mapped_column(nullable=True)
    user_tg_id: Mapped[int] = mapped_column(nullable=True)
    studying_course: Mapped[int]  # 1 or 2

    # many-to-many relationship to Course, bypassing the `UserCourse` class
    courses: Mapped[list["Course"]] = relationship(secondary="user_course", back_populates="students")

    # association between User -> UserCourse -> Course
    course_enrollments: Mapped[list["UserCourse"]] = relationship(back_populates="student")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, user_real_name={self.user_real_name}, user_tg_id={self.user_tg_id})>"


class UserCourse(Base):
    __tablename__ = "user_course"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id"), primary_key=True)

    # association between UserCourse -> User
    student: Mapped["User"] = relationship(back_populates="course_enrollments")

    # association between UserCourse -> Course
    course: Mapped["Course"] = relationship(back_populates="student_enrollments")

    def __repr__(self) -> str:
        return f"<UserCourse(user_id={self.user_id}, course_id={self.course_id})>"


class ClassStatusTable(Base):
    __tablename__ = "class_status"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    classes: Mapped[list["Class"]] = relationship("Class", back_populates="class_status")

    def __repr__(self) -> str:
        return f"<ClassStatusTable(name={self.name})>"


def get_class_status_id(status_name: ClassStatus) -> int:
    for i, name in enumerate(ClassStatus, start=1):
        if name == status_name:
            return i
    raise ValueError(f"Class status {status_name} not found")


class Class(Base):
    __tablename__ = "class"

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id"))
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]
    class_type: Mapped[str] = mapped_column(nullable=True)
    class_status_id: Mapped[int] = mapped_column(
        ForeignKey("class_status.id"), nullable=False, default=get_class_status_id(ClassStatus.need_to_add)
    )
    gcal_event_id: Mapped[str] = mapped_column(nullable=True)

    class_status: Mapped["ClassStatusTable"] = relationship("ClassStatusTable", back_populates="classes")
    course: Mapped["Course"] = relationship("Course", back_populates="classes")

    def __repr__(self) -> str:
        return (
            f"<Class(id={self.id}, course_id={self.course_id}, start_time={self.start_time}, "
            f"end_time={self.end_time}, status={self.class_status}, gcal_event_id={self.gcal_event_id})>"
        )
