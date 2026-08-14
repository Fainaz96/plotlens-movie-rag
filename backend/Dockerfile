FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace
COPY backend /workspace/backend
COPY data /workspace/data
RUN pip install --no-cache-dir /workspace/backend

WORKDIR /workspace/backend
EXPOSE 8100
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8100"]
