FROM python:3.8-slim-buster

# Install psycopg2
RUN apt-get update
RUN apt-get install -y libpq-dev gcc

# upgrade pip
RUN pip install --upgrade pip

# install Python modules needed by the Python app
COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt

COPY . /usr/src/app/

CMD ["python", "/usr/src/app/app_cli.py"]