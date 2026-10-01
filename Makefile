.PHONY: help install build run test clean docker-build docker-run

help:
	@echo "FixLoop Platform Management Makefile"
	@echo "  make install      Install Python dependencies"
	@echo "  make run          Run the Flask application (main.py)"
	@echo "  make test         Execute pytest test suite"
	@echo "  make build        Build application assets and check dependencies"
	@echo "  make docker-build Build Docker container"
	@echo "  make docker-run   Run Docker container"
	@echo "  make clean        Remove cache and temporary files"

install:
	python -m pip install -r requirements.txt

build:
	@echo "Building FixLoop platform..."
	python -c "import app; print('App module validated.')"

run:
	python main.py

test:
	pytest -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docker-build:
	docker build -t fixloop:latest .

docker-run:
	docker run -p 5000:5000 fixloop:latest
