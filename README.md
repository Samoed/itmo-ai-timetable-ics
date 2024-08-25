# itmo-ai-timetable-ics

Генерация файлов .ics с расписанием занятий для студентов ИТМО программы Искусственный интеллект.

## Использование

1. Скачать файл с расписанием в формате .xlsx
   с [диска](https://docs.google.com/spreadsheets/d/1Z4fOC2Hs-5iQ4YZzsZEVxTRsEiCF4AxEnqnv2-rJIMs/edit).
2. Установить зависимости: `pip install -r requirements.txt`
3. Запустить экспорт

   ```bash
   python src/main.py --file <path_to_xlsx> --output <path_to_ics>
   ```

4. Из папки `output` импортировать из папки output расписание с выбранными предметами в любимый календарь.


# Google calendar

1. Create new project in [gcp](https://console.cloud.google.com/cloud-resource-manager)
2. Config consent screen (APIs & Services > OAuth consent screen)
3. Create OAuth 2.0 Client ID (APIs & Services > Credentials)
4. Add user OAuth consent screen
5. Enable Google Calendar API (APIs & Services > Library) ([calendar-json.googleapis.com](https://console.cloud.google.com/apis/library/calendar-json.googleapis.com?))
6. On first run you will be asked to authorize the app in browser open in Chromium (firefox doesn't work)


# DB

1. User
2. list of predmets
3. timetable
4. timetable status
