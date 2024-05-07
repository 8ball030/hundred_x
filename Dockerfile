FROM python:3.11.1
WORKDIR /app

RUN apt-get update && \
    apt-get install -y  cron \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/* && \
    pip install poetry==1.3.2 --no-cache-dir 

ENV POETRY_VIRTUALENVS_IN_PROJECT=true
COPY pyproject.toml ./
RUN poetry install --only main
ENV PATH="/APP/.venv/bin:$PATH"



