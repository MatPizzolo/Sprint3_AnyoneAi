FROM python:3.8.13 AS base


# Append /home/app/.local/bin/ to PATH variable because
# gunicorn is installed there.
ENV PYTHONPATH=/src/

ADD requirements.txt .

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libhdf5-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*
	
RUN pip3 install --upgrade pip && \
    pip3 install \
      --retries 3 \
      --timeout 1000 \
      --no-cache-dir \
      -r requirements.txt

ENV PYTHONPATH=/src/

COPY ./ /src/

WORKDIR /src

FROM base AS test
RUN ["pytest", "-v", "/src/tests"]

FROM base AS build
ENTRYPOINT ["python3", "/src/ml_service.py"]
