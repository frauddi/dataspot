PYTHON_VERSION = 3.11
VENV_NAME = .venv

.PHONY: lint lint-fix check tests clean

lint-fix:
	source $(VENV_NAME)/bin/activate && \
	ruff check . --fix

lint:
	source $(VENV_NAME)/bin/activate && \
	ruff check .

check: lint test

tests:
	source $(VENV_NAME)/bin/activate && \
	python3 -m pytest tests/ -v

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "*.egg" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".coverage" -exec rm -r {} +
	find . -type d -name "htmlcov" -exec rm -r {} +
	find . -type f -name ".DS_Store" -delete
	find . -type f -name ".mypy_cache" -delete
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	find . -type f -name ".ruff_cache" -delete
	find . -type d -name ".ruff_cache" -exec rm -r {} +

venv-clean:
	rm -rf $(VENV_NAME)

venv-create:
	uv venv $(VENV_NAME) --python $(PYTHON_VERSION)

venv-install:
	curl -LsSf https://astral.sh/uv/install.sh | sh

install: venv-create
	source $(VENV_NAME)/bin/activate && \
	uv pip install .

# Handle unknown targets - Support arguments
%:
	@:
