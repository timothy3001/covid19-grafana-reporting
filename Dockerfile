FROM python:3.8.2-alpine3.11

COPY requirements.txt ./
COPY main.py ./
COPY setup.py ./
COPY covid19_grafana_reporting ./covid19_grafana_reporting

RUN pip install -r requirements.txt

CMD ["python", "-u", "./main.py"]