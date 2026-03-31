FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Step 1: Copy only requirements first (best for caching)
# We use './' because Jenkins will already be inside the 'ssss' folder
COPY requirements.txt .

# Step 2: Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Step 3: Copy everything else from the current directory (the 'ssss' folder)
COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
