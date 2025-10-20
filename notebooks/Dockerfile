FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir jupyter jupyterlab ipywidgets

COPY analysis/ /app/analysis/
COPY api/ /app/api/
COPY notebooks/ /app/notebooks/

RUN chmod +x /app/notebooks/start.sh

WORKDIR /app/notebooks

EXPOSE 8888

CMD ["/bin/bash", "/app/notebooks/start.sh"]
