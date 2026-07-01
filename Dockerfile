FROM python:3.12-slim

# Pillow needs a couple of runtime libs for broad image-format support.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo libopenjp2-7 libtiff6 fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY keepstack ./keepstack
COPY web ./web

ENV KEEPSTACK_DATA_DIR=/data \
    KEEPSTACK_HOST=0.0.0.0 \
    KEEPSTACK_PORT=8000
VOLUME ["/data"]
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=4s --start-period=10s \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/healthz').read()==b'ok' else 1)"

CMD ["python", "-m", "keepstack"]
