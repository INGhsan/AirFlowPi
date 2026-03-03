from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

# ============================================================
# Default arguments
# ============================================================
default_args = {
    'owner': 'scouts_dw_admin',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# ============================================================
# Master DAG — 3 stages in strict sequential order:
#   Stage 1 : Staging Area (SA)  — Scout_SA_RUN_run.sh
#   Stage 2 : Dimensions (DW)    — Scout_DW_RUN_methode2_run.sh
#   Stage 3 : Fact tables        — run_FACT_run.sh
# ============================================================
with DAG(
    dag_id='scouts_dw_master_etl',
    default_args=default_args,
    description='Orchestration Talend : SA → DIM → FACT pour le DW Scouts Tunisie',
    # Runs automatically every morning at 08:00 AM. 
    # To change the time, edit this CRON string: 'Minute Hour Day Month DayOfWeek'
    # Example: '30 14 * * *' runs at 14:30 (2:30 PM) every day.
    schedule_interval='0 8 * * *',
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['scouts', 'dw', 'talend'],
) as dag:

    # Base path inside the Docker container (mounted in docker-compose)
    JOB_DIR = '/opt/airflow/talend_jobs'

    # ----------------------------------------------------------
    # STAGE 1 – Staging Area
    # Loads all raw source files into the SA tables in SQL Server.
    # ----------------------------------------------------------
    run_staging_area = BashOperator(
        task_id='run_staging_area',
        bash_command=(
            f'sh {JOB_DIR}/Scout_SA_RUN_run.sh '
        ),
        execution_timeout=timedelta(minutes=60),
    )

    # ----------------------------------------------------------
    # STAGE 2 – Dimensions
    # Reads from SA and populates all dimension tables.
    # ----------------------------------------------------------
    run_dimensions = BashOperator(
        task_id='run_dimensions',
        bash_command=(
            f'sh {JOB_DIR}/Scout_DW_RUN_methode2_run.sh '
        ),
        execution_timeout=timedelta(minutes=60),
    )

    # ----------------------------------------------------------
    # STAGE 3 – Fact Tables
    # Reads from dimensions and populates all fact tables.
    # ----------------------------------------------------------
    run_facts = BashOperator(
        task_id='run_facts',
        bash_command=(
            f'sh {JOB_DIR}/run_FACT_run.sh '
        ),
        execution_timeout=timedelta(minutes=60),
    )

    # ----------------------------------------------------------
    # Pipeline: SA → DIM → FACT  (strict sequential)
    # ----------------------------------------------------------
    run_staging_area >> run_dimensions >> run_facts
