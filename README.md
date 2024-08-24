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
