from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from dqp.run_all import ingest, run_quality

default_args = {
    "owner": "data-team",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="ingestion_quality_pipeline",
    description="Ingestion (CSV/API/DB) -> contrôles qualité -> dbt",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args=default_args,
    tags=["data-quality"],
) as dag:

    t_ingest = PythonOperator(task_id="ingest_sources", python_callable=ingest)

    t_quality = PythonOperator(
        task_id="run_quality_checks",
        python_callable=run_quality,
        op_kwargs={"run_id": "{{ run_id }}"},
    )

    t_dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/dbt && dbt run --profiles-dir .",
    )

    t_dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="cd /opt/airflow/dbt && dbt test --profiles-dir .",
    )

    t_ingest >> t_quality >> t_dbt_run >> t_dbt_test
