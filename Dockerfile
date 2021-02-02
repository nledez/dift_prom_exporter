FROM python:3.7.5

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY main.py ./

EXPOSE 8000
ENTRYPOINT [ "python" ]
CMD [ "main.py" ]
