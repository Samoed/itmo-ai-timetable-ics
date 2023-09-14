# https://github.com/samuelcolvin/pydantic/blob/master/Makefile
.DEFAULT_GOAL := all
poetry = poetry run
isort = isort src/
black = black src/
mypy = mypy src/
flake8  = flake8 src/
pyupgrade = pyupgrade --py310-plus

.PHONY: install-linting
install-linting:
	poetry add flake8 black isort mypy pyupgrade -G dev

.PHONY: format
format:
	$(poetry) $(pyupgrade)
	$(poetry) $(isort)
	$(poetry) $(black)
	#$(poetry) $(mypy)
	$(poetry) $(flake8)

.PHONY: all
all: format
