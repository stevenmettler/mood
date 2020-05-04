FROM python:3.8-slim

RUN pip3 install --upgrade pip

WORKDIR /mood

COPY . /mood

RUN pip3 --no-cache-dir install -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["python3"]
CMD ["app.py"]
