import xlrd
import requests
from covid19_grafana_reporting.settings import DOWNLOAD_PATH, TMP_FOLDER


def download_data(filepath):
    resp = requests.get(DOWNLOAD_PATH)

    with open(filepath, 'wb') as f:
        f.write(resp.content)


def read_data(filepath):
    book = xlrd.open_workbook(filepath)
    sheet = book.sheet_by_index(0)
    num_rows = sheet.nrows - 1

    for i in range(num_rows):
        row_values = sheet.row_values(i)

        if (row_values[1] == 'Germany'):
            date = xlrd.xldate_as_tuple(row_values[0], book.datemode)
            print(str(row_values) + ' ' + str(date))


filepath = f'{TMP_FOLDER}/today.xls'

download_data(filepath)
read_data(filepath)
