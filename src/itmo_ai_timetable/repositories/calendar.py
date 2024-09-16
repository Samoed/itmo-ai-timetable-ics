from datetime import datetime

from gcsa.acl import AccessControlRule, ACLRole, ACLScopeType
from gcsa.calendar import Calendar
from gcsa.event import Event, Visibility
from gcsa.google_calendar import GoogleCalendar
from settings import Settings


class CalendarRepository:
    def __init__(self) -> None:
        self.settings = Settings()

        self.gc = GoogleCalendar(
            credentials_path=self.settings.google_credentials_path, token_path=self.settings.google_token_path
        )

    def get_or_create_calendar(self, calendar_name: str) -> str:
        for calendar in self.gc.get_calendar_list():
            if calendar.summary == calendar_name:
                return calendar.calendar_id
        calendar = Calendar(calendar_name, description=calendar_name)
        calendar = self.gc.add_calendar(calendar)
        self.gc.add_acl_rule(self.get_public_acl(), calendar_id=calendar.calendar_id)
        return calendar.calendar_id

    def get_public_acl(self) -> AccessControlRule:
        return AccessControlRule(
            role=ACLRole.READER,
            scope_type=ACLScopeType.DEFAULT,  # DEFAULT - The public scope
        )

    def add_class_to_calendar(
        self, calendar_id: str, class_name: str, start_datetime: datetime, end_datetime: datetime
    ) -> str:
        event = Event(class_name, start=start_datetime, end=end_datetime, visibility=Visibility.PUBLIC)
        self.gc.add_event(event, calendar_id=calendar_id)
        return event.id

    def delete_class_from_calendar(self, calendar_id: str, event_id: str) -> None:
        self.gc.delete_event(event_id, calendar_id=calendar_id)
