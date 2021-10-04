from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator

from datetime import date, datetime, timedelta
import yfinance as yf
import pandas as pd

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2021,10,1),
    'email': ['aswathkumar07@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

def download_stock_data(stock_ticker):
    start_date = date.today()
    end_date = start_date + timedelta(days=1)
    df = yf.download(stock_ticker, start=start_date, end=end_date, interval='1m')
    df.to_csv(stock_ticker + "_data.csv", header=True)

def get_last_stock_spread():
    apple_data = pd.read_csv("/tmp/data/" + str(date.today()) + "/AAPL_data.csv")
    tesla_data = pd.read_csv("/tmp/data/" + str(date.today()) + "/TSLA_data.csv")
    try:
        spread = [(apple_data['High'][0] + apple_data['Low'][0]) / 2, (tesla_data['High'][0] + tesla_data['Low'][0]) / 2]
        return spread
    except Exception as e:
        return None


with DAG('marketvol', default_args=default_args, schedule_interval='45 18 * * 1-5', description = 'Source Apple and Tesla data') as dag:

    t0 = BashOperator(
        task_id = 'Create_temp_directory',
        bash_command = '''mkdir -p /tmp/data/''' + str(date.today()),
        dag = dag
    )
    
    t1 = PythonOperator(
        task_id = 'AAPL_stock_download',
        python_callable = download_stock_data,
        op_kwargs={'stock_ticker': 'AAPL'},
        dag = dag
    )

    t2 = PythonOperator(
        task_id = 'TSLA_stock_download',
        python_callable = download_stock_data,
        op_kwargs={'stock_ticker': 'TSLA'},
        dag = dag
    )

    t3 = BashOperator(
        task_id = 'Move_APPL_data_to_designated_directory',
        bash_command='''mv /opt/airflow/AAPL_data.csv /tmp/data/''' + str(date.today()) + '/',
        dag = dag
    )

    t4 = BashOperator(
        task_id = 'Move_TSLA_data_to_designated_directory',
        bash_command='''mv /opt/airflow/TSLA_data.csv /tmp/data/''' + str(date.today()) + '/',
        dag = dag
    )
    
    t5 = PythonOperator(
        task_id = 'Run_custom_Python_Query',
        python_callable = get_last_stock_spread,
        dag = dag
    )

t0 >> [t1, t2]
t3 << t1
t4 << t2
[t3,t4] >> t5
