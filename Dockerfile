FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (layer caching)
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy source
COPY ebird_recommend/ ebird_recommend/

EXPOSE 8000

CMD ["uvicorn", "ebird_recommend.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
