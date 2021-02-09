FROM python:alpine

WORKDIR /app
COPY run.py /app

RUN python3 -m pip install boto3 requests
CMD python3 /app/run.py -d $DOMAIN -z $ZONE_ID