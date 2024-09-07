.DEFAULT_GOAL := all
DIRS = src/
pdm = pdm run
mypy = mypy

.PHONY: install
install:
	pdm install -d
	pre-commit install --install-hooks
	pre-commit autoupdate

.PHONY: format
format:
	pdm run lint_local

.PHONY: database
database:
	docker compose up database -d

.PHONY: test
test:
	pdm run test_html

.PHONY: migrate
migrate:
	@read -p "Enter migration message: " message; \
	$(pdm) alembic revision --autogenerate -m "$$message"

.PHONY: downgrade
downgrade:
	$(pdm) alembic downgrade -1

.PHONY: upgrade
upgrade:
	$(pdm) alembic upgrade +1

.PHONY: upgrade-offline
upgrade-offline:
	$(pdm) alembic upgrade head --sql

.PHONY: load_first_course_selection
load_first_course_selection:
	$(pdm) python src/itmo_ai_timetable/cli.py selection --filepath "courses_processor/course_1/Таблица предвыборности.xlsx" \
		--output_path selection_course/course_1.json --sheet_name "Таблица предвыборности" \
		--course_row 3 --first_select_column E --last_select_column AS --course_number 1 --db

.PHONY: load_second_course_selection
load_second_course_selection:
	$(pdm) python src/itmo_ai_timetable/cli.py selection --filepath "courses_processor/course_2/Таблица предвыборности.xlsx" \
		--output_path selection_course/course_2.json --sheet_name "Таблица выборности" \
		--course_row 3 --first_select_column G --last_select_column BB --course_number 2 --db

.PHONY: all
all: format
