.PHONY: run test clean

run:
	docker-compose up --build

test:
	pytest

clean:
	docker-compose down -v
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
