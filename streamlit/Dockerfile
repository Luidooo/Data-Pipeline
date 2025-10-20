#FROM python:3.11-slim
#
#WORKDIR /app
#
#COPY ../requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt
#
#COPY ../analysis/ /app/analysis/
#COPY ../api/ /app/api/
#COPY . /app/streamlit/
#
#WORKDIR /app
#
#EXPOSE 8501
#
#CMD ["streamlit", "run", "streamlit/app.py", "--server.port=8501", "--server.address=0.0.0.0"]

# streamlit/Dockerfile

FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy necessary application folders from the project root
COPY analysis/ /app/analysis/
COPY api/ /app/api/
COPY streamlit/ /app/

# The WORKDIR is now /app, which contains app.py
EXPOSE 8501

# Run the app from the root of the WORKDIR
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
