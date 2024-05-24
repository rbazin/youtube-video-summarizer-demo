FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r ./requirements.txt

COPY ./src/download_model.py /app/download_model.py

ARG TRANSCRIBER_MODEL_NAME="base"
ENV TRANSCRIBER_MODEL_NAME=${TRANSCRIBER_MODEL_NAME}
RUN python download_model.py

COPY ./src/ /app/src/

RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app

USER appuser
CMD ["gunicorn", "--bind", "0.0.0.0:80", "-k", "uvicorn.workers.UvicornWorker", "app:app"]