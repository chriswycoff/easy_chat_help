# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.10-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
# CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
# CMD exec uvicorn --port $PORT --host 0.0.0.0 main:app
# CMD exec gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind :$PORT 
# CMD exec gunicorn --bind :$PORT --workers 12 --worker-class uvicorn.workers.UvicornWorker --threads 8 main:app
# CMD exec gunicorn main:app --worker-class uvicorn.workers.UvicornWorker --bind :$PORT --threads 8
CMD exec gunicorn main:app --worker-class uvicorn.workers.UvicornWorker --bind :$PORT --threads 2 --timeout 0 
