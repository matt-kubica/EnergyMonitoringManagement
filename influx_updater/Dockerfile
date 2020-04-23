FROM python:3.7.6

RUN mkdir /app
WORKDIR /app
ADD . /app/

RUN pip3 install --upgrade pip 
RUN pip3 install pipenv
RUN pipenv install --skip-lock --system --dev