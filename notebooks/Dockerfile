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

RUN mkdir -p /root/.jupyter/lab/user-settings/@jupyterlab/apputils-extension && \
    mkdir -p /root/.jupyter/lab/user-settings/@jupyterlab/notebook-extension && \
    echo '{"theme": "JupyterLab Dark"}' > /root/.jupyter/lab/user-settings/@jupyterlab/apputils-extension/themes.jupyterlab-settings && \
    echo '{"autoStartDefaultKernel": true, "kernelShutdown": false}' > /root/.jupyter/lab/user-settings/@jupyterlab/notebook-extension/tracker.jupyterlab-settings

WORKDIR /app/notebooks

EXPOSE 8888

CMD ["sh", "-c", "sleep 5 && jupyter lab --config=/app/notebooks/jupyter_config.py"]
