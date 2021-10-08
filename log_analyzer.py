from pathlib import Path
import os
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import timedelta, datetime

log_dir = '/opt/airflow/logs/marketvol'

def analyze_file(stock_ticker, log_dir):
    '''
        Prints error and count of errors for individual stock tickers
    '''
    #Getting generator file using rglob command
    olog_files = Path(log_dir).rglob('*.log')
    #Creating list to store errors at later stage
    error_list = []

    #Looping through all log files
    for ofile in list(olog_files):
        file = str(ofile)
        #Checking for marketvol dag and releavnt stock_ticker
        if file.find('marketvol') != -1 and file.find(stock_ticker) != -1:
            file_open = open(file, 'r')
            for ln in file_open:
                if 'ERROR' in ln:
                    error_list.append(ln)

    error_count = len(error_list)
    #Printing total number of errors
    print(f'Total number of errors: {error_count}')
    #Printing the list of errors in case count is greater than zero
    if error_count > 0:
        for error in error_list:
            print(error)

#Setting default arguments for dag
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2021,10,7),
    'email': ['aswathkumar07@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

#Writing DAG initialization
with DAG('log_analyzer', default_args=default_args, schedule_interval='30 3 * * 1-5', description = 'Log of errors in marketvol dag') as dag:
    t1 = PythonOperator(
        task_id = 'AAPL_log_errors',
        python_callable=analyze_file,
        op_kwargs = {'stock_ticker': 'AAPL', 'log_dir': '/opt/airflow/logs/marketvol' }
    )

    t2 = PythonOperator(
        task_id = 'TSLA_log_errors',
        python_callable=analyze_file,
        op_kwargs = {'stock_ticker': 'TSLA', 'log_dir': '/opt/airflow/logs/marketvol' }
    )

t1 >> t2
