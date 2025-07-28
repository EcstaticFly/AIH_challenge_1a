
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libfreetype6-dev \
    libjpeg-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    zlib1g-dev \
    libpng-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

COPY requirements.txt .


RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt


COPY src/ ./src/
COPY extract_outline.py .


RUN mkdir -p /app/input /app/output && \
    chmod 755 /app/input /app/output


RUN chmod +x extract_outline.py


RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser


HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.path.insert(0, '/app/src'); from pdf_extractor_production import ProductionPDFExtractor; print('OK')" || exit 1


ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app/src:/app


CMD ["python", "extract_outline.py"]


LABEL maintainer="PDF Outline Extractor"
LABEL version="1.0"
LABEL description="Production-grade PDF outline extraction service"