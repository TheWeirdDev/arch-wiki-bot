FROM docker.io/python:3.9.5-alpine
WORKDIR /image
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY app.py .
CMD [ "python3", "./app.py" ]
