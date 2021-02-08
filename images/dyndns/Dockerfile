FROM python:alpine

ENV AWS_ACCESS_KEY_ID=""
ENV AWS_SECRET_ACCESS_KEY=""
ENV AWS_SESSION_TOKEN=""

WORKDIR /app
COPY run.py /app

RUN python3 -m pip install boto3 requests
CMD ["python3", "/app/run.py", "-d", "dc1.veraciousdata.io", "-z", "Z04564473TXYVWUJFRVM3"]