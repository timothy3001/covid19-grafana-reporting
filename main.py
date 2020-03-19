import xlrd
import requests
import os
from datetime import datetime, timedelta
from influxdb import InfluxDBClient


def get_download_path(date):
    date_string = date.strftime("%Y-%m-%d")
    download_path = f'https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide-{date_string}.xlsx'
    return download_path


def download_data(filepath):
    date = datetime.now()
    resp = requests.get(get_download_path(date))

    if resp.status_code != 200:
        date = date.now() - timedelta(days=1)
        resp = requests.get(get_download_path(date))

    with open(filepath, 'wb') as f:
        f.write(resp.content)


def filter_country(sheet):
    result_rows = []
    num_rows = sheet.nrows

    for i in range(num_rows):
        row_values = sheet.row_values(i)
        if row_values[country_column] == country_string:
            result_rows.append(row_values)

    return result_rows


def read_country_data(filepath):
    book = xlrd.open_workbook(filepath)
    sheet = book.sheet_by_index(0)
    return filter_country(sheet)


def get_data_tuples(rows):
    global new_confirmed_column
    global new_deaths_column
    # global new_recovered_column

    data_tuples = []

    for r in rows:
        date = xlrd.xldate_as_datetime(r[0], 0)  # Datemode: 0 seems to be OK

        data_tuples.append({
            'date': date.strftime("%Y-%m-%d") + 'T00:00:00Z',
            'new_confirmed': r[new_confirmed_column],
            'new_deaths': r[new_deaths_column],
            # 'new_recoverd': r[new_recovered_column]
        })

    return data_tuples


def post_data_to_influx(data_tuples):
    global influx_host
    global influx_port
    global influx_db
    global influx_user
    global influx_user_password

    client = InfluxDBClient(host=influx_host, port=influx_port,
                            username=influx_user, password=influx_user_password)
    client.create_database(influx_db)

    data_points = []

    for d in data_tuples:
        data_points.append({
            'measurement': 'covid19Measurement',
            'tags': {},
            'time': d['date'],
            'fields': {
                'new_confirmed': d['new_confirmed'],
                'new_deaths': d['new_deaths']
            }
        })

    client.write_points(data_points, database=influx_db)


filepath = f'tmp/today.xlsx'

influx_host = os.environ['INFLUXDB_HOST']
influx_port = int(os.environ['INFLUXDB_PORT'])
influx_user = os.environ['INFLUXDB_USER']
influx_user_password = os.environ['INFLUXDB_USER_PASSWORD']
influx_db = os.environ['INFLUXDB_DBNAME']
country_string = os.environ['COUNTRY_STRING']
country_column = int(os.environ['COUNTRY_COLUMN'])
date_column = int(os.environ['DATE_COLUMN'])
new_confirmed_column = int(os.environ['NEW_CONFIRMED_COLUMN'])
new_deaths_column = int(os.environ['NEW_DEATHS_COLUMN'])
# new_recovered_column = int(os.environ['NEW_RECOVERED_COLUMN'])

download_data(filepath)
data_rows = read_country_data(filepath)
data_tuples = get_data_tuples(data_rows)
post_data_to_influx(data_tuples)
