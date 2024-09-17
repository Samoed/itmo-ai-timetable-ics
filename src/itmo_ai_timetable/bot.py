import html
import json
import traceback
from datetime import time

import pytz
from logger import get_logger
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from itmo_ai_timetable.repositories.calendar import CalendarRepository
from itmo_ai_timetable.repositories.db import DBRepository
from itmo_ai_timetable.schedule_parser import ScheduleParser
from itmo_ai_timetable.settings import Settings

logger = get_logger(__name__)
settings = Settings()


async def sync_courses_table(context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(settings.admin_chat_id, "Start sync table")
    for i, (excel_url, list_name) in enumerate(settings.get_calendar_settings()):
        logger.info(f"Start sync {list_name}")
        parser = ScheduleParser(excel_url, list_name)
        pairs = parser.parse()
        not_found = await DBRepository.add_classes(pairs)
        if not_found:
            logger.warning(f"Classes not found: {not_found}")
            not_found_str = [f"- {pair}\n" for pair in not_found]
            await context.bot.send_message(
                settings.admin_chat_id,
                f"Classes not found: {not_found_str}\nКурс: {i}",
            )
            continue
        logger.info(f"End sync {list_name}")
    await context.bot.send_message(settings.admin_chat_id, "Sync finished table")


async def update_classes_calendar(context: ContextTypes.DEFAULT_TYPE) -> None:  # noqa: ARG001
    courses = await DBRepository.get_courses()
    calendar_repo = CalendarRepository()

    for course in courses:
        if course.name not in ["Этика искусственного интеллекта", "Продвинутый курс научных исследований"]:
            continue
        if course.timetable_id is None:
            course.timetable_id = calendar_repo.get_or_create_calendar(course.name)
            await DBRepository.update_courses([course])
        classes = await DBRepository.get_unsynced_classes_for_course(course)
        for class_ in classes:
            class_.gcal_event_id = calendar_repo.add_class_to_calendar(
                course.timetable_id, course.name, class_.start_time, class_.end_time
            )
            class_.class_status_id = 5
        await DBRepository.update_classes(classes)


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  # noqa: ARG001
    """Ping bot."""
    if update.message is None:
        return
    logger.info(f"Ping {update.message.chat.id}")
    await update.message.reply_text("Pong")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/errorhandlerbot.py
    logger.error("Exception while handling an update:", exc_info=context.error)

    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        "An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )
    await context.bot.send_message(settings.admin_chat_id, text=message, parse_mode=ParseMode.HTML)


def add_handlers(application: Application) -> None:
    application.add_handler(CommandHandler("ping", ping))


def add_jobs(application: Application, time_zone_str: str) -> None:
    time_zone = pytz.timezone(time_zone_str)
    if application.job_queue is None:
        raise ValueError("Job queue is None")
    application.job_queue.run_daily(sync_courses_table, time=time(8, tzinfo=time_zone))
    application.job_queue.run_repeating(update_classes_calendar, interval=60)


def main() -> None:
    """Start the bot."""
    logger.info("start bot")

    application = Application.builder().token(settings.tg_bot_token).post_init(sync_courses_table).build()

    add_handlers(application)
    add_jobs(application, settings.tz)
    application.add_error_handler(error_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
