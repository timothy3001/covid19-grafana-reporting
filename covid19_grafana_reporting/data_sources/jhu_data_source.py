import os
import csv
import requests
from covid19_grafana_reporting.data_sources.data_source_interface import DataSourceInterface
from datetime import datetime

DOWNLOAD_CONFIRMED = os.environ['DOWNLOAD_LINK_CONFIRMED']
DOWNLOAD_DEATHS = os.environ['DOWNLOAD_LINK_DEATHS']
DOWNLOAD_RECOVERED = os.environ['DOWNLOAD_LINK_RECOVERED']
FILEPATH_CONFIRMED = "./tmp/today_confirmed.csv"
FILEPATH_DEATHS = "./tmp/today_deaths.csv"
FILEPATH_RECOVERED = "./tmp/today_recovered.csv"

country_string = os.environ['COUNTRY_STRING']
country_column = int(os.environ['COUNTRY_COLUMN'])
first_date_column = int(os.environ['FIRST_DATE_COLUMN'])


# Data source John Hopkins University. Retrieved from git repo
class JhuDataSource(DataSourceInterface):

    def get_data_tuples(self):
        self.download_data()

        confirmed_rows = self.read_csv_file(FILEPATH_CONFIRMED)
        death_rows = self.read_csv_file(FILEPATH_DEATHS)
        recovered_rows = self.read_csv_file(FILEPATH_RECOVERED)

        confirmed_data = self.extract_country_data(confirmed_rows)
        deaths_data = self.extract_country_data(death_rows)
        recovered_data = self.extract_country_data(recovered_rows)

        return self.combine_all_data(confirmed_data, deaths_data, recovered_data)

    def combine_all_data(self, confirmed_data, deaths_data, recovered_data):
        containing_most = confirmed_data
        if (len(deaths_data) > len(containing_most)):
            containing_most = deaths_data
        if (len(recovered_data) > len(containing_most)):
            containing_most = recovered_data

        confirmed_before = 0
        deaths_before = 0
        recovered_before = 0

        result_data_tuples = []

        for d in containing_most:
            date = datetime.strptime(d, '%m/%d/%y')

            new_confirmed = 0
            new_deaths = 0
            new_recovered = 0
            total_confirmed = 0
            total_deaths = 0
            total_recovered = 0

            if d in confirmed_data:
                total_confirmed = int(confirmed_data[d])
                new_confirmed = int(confirmed_data[d]) - confirmed_before
                confirmed_before = int(confirmed_data[d])
            if d in deaths_data:
                total_deaths = int(deaths_data[d])
                new_deaths = int(deaths_data[d]) - deaths_before
                deaths_before = int(deaths_data[d])
            if d in recovered_data:
                total_recovered = int(recovered_data[d])
                new_recovered = int(recovered_data[d]) - recovered_before
                recovered_before = int(recovered_data[d])

            result_data_tuples.append({
                'date': date,
                'new_confirmed': new_confirmed,
                'new_deaths': new_deaths,
                'new_recovered': new_recovered,
                'total_confirmed': total_confirmed,
                'total_deaths': total_deaths,
                'total_recovered': total_recovered
            })

        return result_data_tuples

    def read_csv_file(self, filepath):
        result_rows = []
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            for r in reader:
                result_rows.append(r)

        return result_rows

    def extract_country_data(self, rows):
        first_row = rows[0]

        country_row = None

        for r in rows:
            if r[country_column] == country_string:
                country_row = r
                break

        if (country_row == None):
            raise Exception(f'No row for country {country_string} found!')

        data_columns = country_row[first_date_column:]
        date_columns = first_row[first_date_column:]

        result_dict = {}

        for i in range(len(data_columns)):
            c_date = date_columns[i]
            c_data = data_columns[i]

            result_dict[c_date] = c_data

        return result_dict

    def download_data(self):
        resp_confirmed = requests.get(DOWNLOAD_CONFIRMED)
        resp_deaths = requests.get(DOWNLOAD_DEATHS)
        resp_recovered = requests.get(DOWNLOAD_RECOVERED)

        with open(FILEPATH_CONFIRMED, 'wb') as f:
            f.write(resp_confirmed.content)

        with open(FILEPATH_DEATHS, 'wb') as f:
            f.write(resp_deaths.content)

        with open(FILEPATH_RECOVERED, 'wb') as f:
            f.write(resp_recovered.content)
