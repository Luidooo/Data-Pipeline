#!/bin/bash

mkdir -p /root/.jupyter/lab/user-settings/@jupyterlab/apputils-extension
mkdir -p /root/.jupyter/lab/user-settings/@jupyterlab/notebook-extension

cat >/root/.jupyter/lab/user-settings/@jupyterlab/apputils-extension/themes.jupyterlab-settings <<EOF
{
    "theme": "JupyterLab Dark"
}
EOF

cat >/root/.jupyter/lab/user-settings/@jupyterlab/notebook-extension/tracker.jupyterlab-settings <<EOF
{
    "autoStartDefaultKernel": true,
    "kernelShutdown": false
}
EOF

#waiting db
sleep 5

jupyter lab --config=/app/notebooks/jupyter_config.py
