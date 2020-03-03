FROM python

RUN python -m pip install --upgrade pip setuptools wheel

RUN pip install flask mysql-connector-python

ADD ./airplane_service/airplane.py /app/airplane.py

WORKDIR /app

EXPOSE 9000

CMD ["python", "airplane.py"]