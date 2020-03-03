FROM python

RUN python -m pip install --upgrade pip setuptools wheel

RUN pip install flask mysql-connector-python

ADD ./admin_service/admin.py /app/admin.py

WORKDIR /app

EXPOSE 6000

CMD ["python", "admin.py"]