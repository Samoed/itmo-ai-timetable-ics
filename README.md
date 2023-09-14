# itmo-ai-timetable-ics

Генерация файлов .ics с расписанием занятий для студентов ИТМО программы Искусственный интеллект.

## Использование

1. Скачать файл с расписанием в формате .xlsx
   с [диска](https://docs.google.com/spreadsheets/d/13FigeqcqbtgnFAfFIyxz440SOIy3DeS2Z6aTQDNBJw4/edit).
2. Установить зависимости: `pip install -r requirements.txt`
3. Запустить экспорт

   ```bash
   python main.py --input <path_to_xlsx> --output <path_to_ics>
   ```

4. Из папки `output` импортировать из папки output расписание с выбранными предметами в любимый календарь.
