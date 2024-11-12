FROM python:3.12-slim
LABEL authors="dimaboro"
WORKDIR /app
RUN pip install --no-cache-dir poetry
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-dev
COPY . .
CMD ["python", "main.py"]
