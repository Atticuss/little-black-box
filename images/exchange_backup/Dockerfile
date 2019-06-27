FROM python:3-alpine
RUN pip3 install boto3 
ADD backup.py /backup.py
ENTRYPOINT python3 backup.py