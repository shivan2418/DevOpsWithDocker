FROM python:3.7.12-buster

COPY requirements.txt ./
RUN /usr/local/bin/python -m pip install --upgrade pip && pip install -r requirements.txt

CMD ["python","/app/update_tester.py"]