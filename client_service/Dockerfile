FROM python

RUN python -m pip install --upgrade pip setuptools wheel

RUN pip install requests

ADD ./client_service/client.py /app/client.py

WORKDIR /app

CMD ["python", "client.py"]