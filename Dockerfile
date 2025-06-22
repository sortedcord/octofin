# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Prevents Python from writing pyc files to disk and buffers
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y ffmpeg

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files (including the octofin Django project)
COPY . /app/

EXPOSE 8193

RUN python /app/octofin/manage.py makemigrations
RUN python /app/octofin/manage.py migrate

# Use Gunicorn as the entrypoint, point to the wsgi.py inside the Django project
CMD ["gunicorn", "--chdir", "octofin", "--bind", "0.0.0.0:8193", "octofin.wsgi:application"]
