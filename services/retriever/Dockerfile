FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY services/retriever/requirements.txt /tmp/retriever-requirements.txt
COPY services/embedder/requirements.txt /tmp/embedder-requirements.txt
RUN pip install --no-cache-dir -r /tmp/retriever-requirements.txt -r /tmp/embedder-requirements.txt

COPY . /app

CMD ["python", "-m", "services.retriever.api_main"]
