FROM python:3.9

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY tdpt .

VOLUME /config

ENTRYPOINT [ "python", "__main__.py"]
CMD ["--config", "/config/tdpt.ini"]
