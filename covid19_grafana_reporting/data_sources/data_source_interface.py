
class DataSourceInterface:
    def get_data_tuples():
        """ Returns current data tuples as list of:
            {
                'date': date.strftime("%Y-%m-%d") + 'T00:00:00Z',
                'new_confirmed': r[new_confirmed_column],
                'new_deaths': r[new_deaths_column],
                'new_recoverd': r[new_recovered_column]
            }
        """
        pass
