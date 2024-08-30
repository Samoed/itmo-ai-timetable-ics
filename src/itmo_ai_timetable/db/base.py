import enum
from datetime import datetime

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)


class Course(Base):
    __tablename__ = "course"

    name: Mapped[str]
    meeting_link: Mapped[str] = mapped_column(nullable=True)
    course_info_link: Mapped[str] = mapped_column(nullable=True)
    chat_link: Mapped[str] = mapped_column(nullable=True)
    timetable_id: Mapped[str] = mapped_column(nullable=True)

    users: Mapped[list["User"]] = relationship("User", secondary="user_course", back_populates="courses")
    classes: Mapped[list["Class"]] = relationship("Class", back_populates="course")

    def __repr__(self) -> str:
        return (
            f"<Course(id={self.id}, name={self.name}, meeting_link={self.meeting_link}, "
            f"notion_link={self.course_info_link}, tg_chat_link={self.chat_link}, timetable_id={self.timetable_id})>"
        )


class User(Base):
    __tablename__ = "user"

    user_real_name: Mapped[str] = mapped_column(nullable=True)
    user_tg_id: Mapped[int] = mapped_column(nullable=True)

    courses: Mapped[list["Course"]] = relationship("Course", secondary="user_course", back_populates="users")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, user_real_name={self.user_real_name}, user_tg_id={self.user_tg_id})>"


class UserCourse(Base):
    __tablename__ = "user_course"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id"), primary_key=True)

    user: Mapped["User"] = relationship("User", back_populates="user_courses")
    course: Mapped["Course"] = relationship("Course", back_populates="user_courses")

    def __repr__(self) -> str:
        return f"<UserCourse(user_id={self.user_id}, course_id={self.course_id})>"


class ClassStatus(enum.Enum):
    need_to_delete = "need_to_delete"
    deleted = "deleted"
    need_to_update = "need_to_update"
    synced = "synced"


class Class(Base):
    __tablename__ = "class"

    course_id: Mapped[int] = mapped_column(ForeignKey("course.id"))
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]
    class_status: Mapped[ClassStatus] = mapped_column(Enum(ClassStatus), default=ClassStatus.need_to_update)

    course: Mapped["Course"] = relationship("Course", back_populates="classes")

    def __repr__(self) -> str:
        return (
            f"<Class(id={self.id}, course_id={self.course_id}, start_time={self.start_time}, "
            f"end_time={self.end_time}, status={self.class_status})>"
        )
