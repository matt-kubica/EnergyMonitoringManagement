FROM python:3.7.6
ADD . /app
WORKDIR /app

RUN pip3 install --upgrade pip
RUN pip install pipenv
RUN pipenv install --skip-lock --system --dev
