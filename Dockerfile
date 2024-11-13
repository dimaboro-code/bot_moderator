FROM python:3.12-slim
LABEL authors="dimaboro"
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir poetry
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-root --no-dev
COPY . ./
CMD ["poetry", "run", "python", "main.py"]
