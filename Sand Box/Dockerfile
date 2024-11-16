# Use Python 3.12 as the base image
FROM python:3.12-slim

# Set the working directory
WORKDIR /usr/src/app

# Copy the requirements file to docker image
COPY requirements.txt ./

RUN apt-get update \
&& pip3 install -r requirements.txt --no-cache-dir

# Copy the application code to the image
COPY app/ ./

# Run FastAPI CLI to start the application
CMD ["fastapi", "dev", "main.py", "--host", "0.0.0.0", "--reload", "--port", "8000"]
