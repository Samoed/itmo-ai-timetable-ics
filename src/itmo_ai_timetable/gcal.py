# import os
#
# os.environ["TZ"] = "Europe/Moscow"
#
# from datetime import datetime, timedelta
#
# from gcsa.calendar import Calendar
# from gcsa.event import Event
# from gcsa.google_calendar import GoogleCalendar
#
# gc = GoogleCalendar(credentials_path="")
#
#
# calendar = Calendar(
#     "New calendar very new calendarffffffffffffffffffffffffff", description="Calendar for travel related events"
# )
# calendar = gc.add_calendar(calendar)
# now = datetime.now()
# start = now + timedelta(days=1)
# end = start + timedelta(hours=2)
# event = Event("Meeting", start=start, end=end)
# event = gc.add_event(event, calendar_id=calendar.calendar_id)
# print(event)
