from datetime import datetime

from sqlalchemy import ForeignKey
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

    # many-to-many relationship to Child, bypassing the `Association` class
    children: Mapped[list["User"]] = relationship(secondary="user_course", back_populates="parents", viewonly=True)

    # association between Parent -> Association -> Child
    child_associations: Mapped[list["UserCourse"]] = relationship(back_populates="parent")
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

    # many-to-many relationship to Parent, bypassing the `Association` class
    parents: Mapped[list["Course"]] = relationship(secondary="user_course", back_populates="children", viewonly=True)

    # association between Child -> Association -> Parent
    parent_associations: Mapped[list["UserCourse"]] = relationship(back_populates="child")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, user_real_name={self.user_real_name}, user_tg_id={self.user_tg_id})>"


class UserCourse(Base):
    __tablename__ = "user_course"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id"), primary_key=True)

    # association between Association -> Child
    child: Mapped["User"] = relationship(back_populates="parent_associations")

    # association between Association -> Parent
    parent: Mapped["Course"] = relationship(back_populates="child_associations")

    def __repr__(self) -> str:
        return f"<UserCourse(user_id={self.user_id}, course_id={self.course_id})>"


class ClassStatusTable(Base):
    __tablename__ = "class_status"

    name: Mapped[str]
    classes: Mapped[list["Class"]] = relationship("Class", back_populates="class_status")

    def __repr__(self) -> str:
        return f"<ClassStatusTable(name={self.name})>"


class Class(Base):
    __tablename__ = "class"

    course_id: Mapped[int] = mapped_column(ForeignKey("course.id"))
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]
    class_status_id: Mapped[id] = mapped_column(ForeignKey("class_status.id"), nullable=False, default=1)
    class_status: Mapped["ClassStatusTable"] = relationship("ClassStatusTable", back_populates="classes")

    course: Mapped["Course"] = relationship("Course", back_populates="classes")

    def __repr__(self) -> str:
        return (
            f"<Class(id={self.id}, course_id={self.course_id}, start_time={self.start_time}, "
            f"end_time={self.end_time}, status={self.class_status})>"
        )
