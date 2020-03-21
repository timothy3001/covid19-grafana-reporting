import xlrd
import requests
import os
import crython
from datetime import datetime, timedelta
from influxdb import InfluxDBClient
from covid19_grafana_reporting.data_sources.jhu_data_source import JhuDataSource


def post_data_to_influx(data_tuples):
    global influx_host
    global influx_port
    global influx_db
    global influx_user
    global influx_user_password

    try:
        client = InfluxDBClient(host=influx_host, port=influx_port,
                                username=influx_user, password=influx_user_password)
        client.create_database(influx_db)

        data_points = []

        for d in data_tuples:
            data_points.append({
                'measurement': 'covid19Measurement',
                'tags': {},
                'time': d['date'].strftime("%Y-%m-%d") + 'T00:00:00Z',
                'fields': {
                    'new_confirmed': d['new_confirmed'],
                    'new_deaths': d['new_deaths'],
                    'new_recovered': d['new_recovered']
                }
            })

        client.write_points(data_points, database=influx_db)
    finally:
        client.close()


@crython.job(expr='@hourly')
def execute():
    try:
        print("Updating covid-19 data...")
        data_source = JhuDataSource()

        data_tuples = data_source.get_data_tuples()
        post_data_to_influx(data_tuples)
        print("Done updating!")
    except Exception as e:
        print("Error occured: ")
        print(e)


filepath = f'tmp/today.xlsx'

influx_host = os.environ['INFLUXDB_HOST']
influx_port = int(os.environ['INFLUXDB_PORT'])
influx_user = os.environ['INFLUXDB_USER']
influx_user_password = os.environ['INFLUXDB_USER_PASSWORD']
influx_db = os.environ['INFLUXDB_DBNAME']

print("Starting up...")
print("Running updater immediately...")
execute()
crython.start()
print("Starting cron job...")
crython.join()
