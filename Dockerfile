FROM python:3
# prevent saving .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /backend
# this directory contains requirements.txt  
COPY requirements.txt /backend
RUN pip install -r requirements.txt
COPY . /backend/