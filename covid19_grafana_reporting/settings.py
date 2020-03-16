from datetime import datetime


def datestring():
    return datetime.now().strftime("%Y-%m-%d")


DOWNLOAD_PATH = f'https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide-{datestring()}.xls'
TMP_FOLDER = './tmp'
