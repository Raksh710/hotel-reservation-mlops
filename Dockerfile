# Containerizes the entire project (the one in custom_jenkins only builds the Jenkins image)
# Pin the Python version so pandas/numpy/scikit-learn install from prebuilt wheels
FROM python:3.12-slim

# Prevent .pyc files and keep Python output unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies required by LightGBM
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the application code
COPY . .

# Install the package in editable mode
RUN pip install --no-cache-dir -e .

# Train the model before running the application.
# The GCP key is mounted only for this step and is never stored in an image layer.
RUN --mount=type=secret,id=gcp_key,target=/run/secrets/gcp_key.json \
    GOOGLE_APPLICATION_CREDENTIALS=/run/secrets/gcp_key.json \
    python pipeline/training_pipeline.py

# Expose the port that Flask will run on
EXPOSE 5000

# Command to run the app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]