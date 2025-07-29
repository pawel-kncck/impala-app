# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

#
# --- FIX FOR OLD DEBIAN REPOSITORIES ---
# The Debian "Buster" repositories have been moved to the archive.
# We need to update the sources.list to point to the new location.
#
RUN echo "deb http://archive.debian.org/debian/ buster main" > /etc/apt/sources.list && \
    echo "deb http://archive.debian.org/debian-security buster/updates main" >> /etc/apt/sources.list && \
    echo "deb http://archive.debian.org/debian/ buster-updates main" >> /etc/apt/sources.list

#
# --- INSTALL CURL FOR HEALTHCHECKS ---
#
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run Gunicorn when the container launches
CMD ["gunicorn", "main:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:5000"]