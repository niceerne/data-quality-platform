.PHONY: up down test run dbt-run

up:
	docker compose up -d --build

down:
	docker compose down

test:
	PYTHONPATH=src pytest -q

run:
	PYTHONPATH=src python -m dqp.run_all

dbt-run:
	cd dbt && dbt run --profiles-dir . && dbt test --profiles-dir .
