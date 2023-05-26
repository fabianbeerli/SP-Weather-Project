FROM python:3.10.4

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        && \
    rm -rf /var/lib/apt/lists/*

# Install project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install ipywidgets
RUN pip install ipywidgets
RUN pip install scipy

# Copy the rest of the application files to the working directory
COPY . .

# Set the command to run your application
CMD ["python", "app.py"]

