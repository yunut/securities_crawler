FROM python:3.11
WORKDIR /securities-crawler
COPY ./requirements.txt /securities-crawler
RUN pip install --no-cache-dir --upgrade -r /securities-crawler/requirements.txt
COPY ./src /securities-crawler/src
ENV PYTHONPATH=/securities-crawler/src
WORKDIR /securities-crawler/src
CMD ["uvicorn", "main:crawler", "--host", "0.0.0.0", "--port", "80"]